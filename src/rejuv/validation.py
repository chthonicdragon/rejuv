from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final

from jsonschema import Draft202012Validator, FormatChecker

from rejuv.models import InterventionEpisode
from rejuv.releases import DataReleaseManifest
from rejuv.sources import SourceManifest
from rejuv.versioning import ContractKind


VALIDATION_PROFILE_VERSION: Final[str] = "0.1.0"

type JSONValue = dict[str, Any] | list[Any] | str | int | float | bool | None
type PathPart = str | int


class ValidationLayer(StrEnum):
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    layer: ValidationLayer
    path: tuple[PathPart, ...]
    message: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    contract_kind: ContractKind
    contract_version: str
    validation_profile_version: str
    issues: tuple[ValidationIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues

    @property
    def structural_valid(self) -> bool:
        return not any(issue.layer is ValidationLayer.STRUCTURAL for issue in self.issues)

    @property
    def semantic_valid(self) -> bool:
        return not any(issue.layer is ValidationLayer.SEMANTIC for issue in self.issues)


def _patch_http_urls(node: Any) -> None:
    if isinstance(node, dict):
        if node.get("format") == "uri":
            node["pattern"] = "^https?://"
        for value in node.values():
            _patch_http_urls(value)
    elif isinstance(node, list):
        for value in node:
            _patch_http_urls(value)


def _patch_checksum_schema(schema: dict[str, Any]) -> None:
    checksum = schema.get("$defs", {}).get("Checksum")
    if not isinstance(checksum, dict):
        return
    properties = checksum.get("properties", {})
    if not isinstance(properties, dict):
        return

    algorithm = properties.get("algorithm")
    if isinstance(algorithm, dict):
        algorithm["const"] = "sha256"

    digest = properties.get("digest")
    if isinstance(digest, dict):
        digest["pattern"] = "^[0-9A-Fa-f]{64}$"


def _patch_evidence_source_pointer(schema: dict[str, Any]) -> None:
    evidence = schema.get("$defs", {}).get("EvidenceReference")
    if not isinstance(evidence, dict):
        return

    evidence["allOf"] = [
        {
            "if": {
                "properties": {"source_type": {"not": {"const": "synthetic"}}},
                "required": ["source_type"],
            },
            "then": {
                "anyOf": [
                    {
                        "required": ["doi"],
                        "properties": {"doi": {"type": "string", "minLength": 1}},
                    },
                    {
                        "required": ["pmid"],
                        "properties": {"pmid": {"type": "string", "minLength": 1}},
                    },
                    {
                        "required": ["accession"],
                        "properties": {"accession": {"type": "string", "minLength": 1}},
                    },
                    {
                        "required": ["url"],
                        "properties": {
                            "url": {
                                "type": "string",
                                "format": "uri",
                                "minLength": 1,
                            }
                        },
                    },
                ]
            },
        }
    ]


def strict_intervention_episode_schema() -> dict[str, Any]:
    schema = deepcopy(InterventionEpisode.model_json_schema())
    schema["x-rejuv-validation-profile-version"] = VALIDATION_PROFILE_VERSION
    _patch_http_urls(schema)
    _patch_evidence_source_pointer(schema)
    return schema


def strict_source_manifest_schema() -> dict[str, Any]:
    schema = deepcopy(SourceManifest.model_json_schema())
    schema["x-rejuv-validation-profile-version"] = VALIDATION_PROFILE_VERSION
    _patch_http_urls(schema)
    _patch_checksum_schema(schema)
    return schema


def strict_data_release_manifest_schema() -> dict[str, Any]:
    schema = deepcopy(DataReleaseManifest.model_json_schema())
    schema["x-rejuv-validation-profile-version"] = VALIDATION_PROFILE_VERSION
    _patch_checksum_schema(schema)
    return schema


def validation_profile() -> dict[str, Any]:
    return {
        "profile_version": VALIDATION_PROFILE_VERSION,
        "record_contracts": {
            "intervention_episode": "0.1.0",
            "source_manifest": "0.1.0",
            "data_release_manifest": "0.1.0",
        },
        "rule_policy": {
            "json_schema": (
                "Portable structural constraints plus selected cross-field constraints "
                "that JSON Schema 2020-12 can express safely."
            ),
            "semantic_engine": (
                "Stable rule ids for cross-record, referential, ordering, and graph "
                "invariants. Critical portable rules may be checked here too so callers "
                "receive a stable rule id."
            ),
        },
        "rules": [
            {
                "rule_id": "EVIDENCE_SOURCE_POINTER_REQUIRED",
                "contract": "intervention_episode",
                "enforced_by": ["json_schema", "semantic_engine", "pydantic_reader"],
                "description": (
                    "Non-synthetic evidence must provide at least one DOI, PMID, "
                    "accession, or URL."
                ),
            },
            {
                "rule_id": "INTERVENTION_ORDER_UNIQUE",
                "contract": "intervention_episode",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "Intervention order values must be unique.",
            },
            {
                "rule_id": "INTERVENTION_ORDER_ASCENDING",
                "contract": "intervention_episode",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "Interventions must be serialized in ascending order.",
            },
            {
                "rule_id": "EVIDENCE_REFERENCE_RESOLVES",
                "contract": "intervention_episode",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "Every evidence_ids entry must resolve to declared evidence.",
            },
            {
                "rule_id": "CHECKSUM_SHA256_ONLY",
                "contract": "data_release_manifest",
                "enforced_by": ["json_schema", "pydantic_reader"],
                "description": "Checksum algorithm is sha256 in contract 0.1.0.",
            },
            {
                "rule_id": "CHECKSUM_HEX_64",
                "contract": "data_release_manifest",
                "enforced_by": ["json_schema", "pydantic_reader"],
                "description": "SHA-256 digest is exactly 64 hexadecimal characters.",
            },
            {
                "rule_id": "RELEASE_SOURCE_IDS_UNIQUE",
                "contract": "data_release_manifest",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "Source ids are unique within a release.",
            },
            {
                "rule_id": "RELEASE_ARTIFACT_IDS_UNIQUE",
                "contract": "data_release_manifest",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "Artifact ids are unique within a release.",
            },
            {
                "rule_id": "RELEASE_ARTIFACT_SOURCE_RESOLVES",
                "contract": "data_release_manifest",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "Every artifact source_id resolves to a declared source.",
            },
            {
                "rule_id": "RELEASE_SOURCE_VERSION_MATCH",
                "contract": "data_release_manifest",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "Artifact source_version matches the source snapshot version.",
            },
            {
                "rule_id": "RELEASE_DERIVATION_ARTIFACT_RESOLVES",
                "contract": "data_release_manifest",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "Every derivation source_artifact_id resolves.",
            },
            {
                "rule_id": "RELEASE_RECORD_LINEAGE_MATCH",
                "contract": "data_release_manifest",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "Derivation source_record_id matches its source artifact.",
            },
            {
                "rule_id": "RELEASE_EPISODE_SCHEMA_MATCH",
                "contract": "data_release_manifest",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "Episode reference schema versions match the release.",
            },
            {
                "rule_id": "RELEASE_EPISODE_IDS_UNIQUE",
                "contract": "data_release_manifest",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "Episode ids are unique across release derivations.",
            },
            {
                "rule_id": "RELEASE_EPISODE_COUNT_MATCH",
                "contract": "data_release_manifest",
                "enforced_by": ["semantic_engine", "pydantic_reader"],
                "description": "episode_count equals normalized episode references.",
            },
        ],
    }


def _structural_issues(
    payload: JSONValue,
    schema: dict[str, Any],
) -> list[ValidationIssue]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    return [
        ValidationIssue(
            code=f"JSON_SCHEMA_{error.validator.upper()}",
            layer=ValidationLayer.STRUCTURAL,
            path=tuple(error.absolute_path),
            message=error.message,
        )
        for error in errors
    ]


def _evidence_pointer_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for index, evidence in enumerate(payload.get("evidence", [])):
        if not isinstance(evidence, dict):
            continue
        if evidence.get("source_type") == "synthetic":
            continue
        if any(evidence.get(key) for key in ("doi", "pmid", "accession", "url")):
            continue
        issues.append(
            ValidationIssue(
                code="EVIDENCE_SOURCE_POINTER_REQUIRED",
                layer=ValidationLayer.SEMANTIC,
                path=("evidence", index),
                message=(
                    "Non-synthetic evidence requires at least one DOI, PMID, "
                    "accession, or URL."
                ),
            )
        )
    return issues


def _episode_semantic_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    issues = _evidence_pointer_issues(payload)
    interventions = payload.get("interventions", [])
    orders = [
        item.get("order")
        for item in interventions
        if isinstance(item, dict) and isinstance(item.get("order"), int)
    ]

    if len(orders) != len(set(orders)):
        issues.append(
            ValidationIssue(
                code="INTERVENTION_ORDER_UNIQUE",
                layer=ValidationLayer.SEMANTIC,
                path=("interventions",),
                message="Intervention order values must be unique.",
            )
        )
    if orders != sorted(orders):
        issues.append(
            ValidationIssue(
                code="INTERVENTION_ORDER_ASCENDING",
                layer=ValidationLayer.SEMANTIC,
                path=("interventions",),
                message="Interventions must be serialized in ascending order.",
            )
        )

    evidence = payload.get("evidence", [])
    known = {
        item.get("evidence_id")
        for item in evidence
        if isinstance(item, dict) and isinstance(item.get("evidence_id"), str)
    }

    for collection in ("baseline", "interventions", "outcomes", "adverse_effects"):
        for index, item in enumerate(payload.get(collection, [])):
            if not isinstance(item, dict):
                continue
            for ref_index, evidence_id in enumerate(item.get("evidence_ids", [])):
                if isinstance(evidence_id, str) and evidence_id not in known:
                    issues.append(
                        ValidationIssue(
                            code="EVIDENCE_REFERENCE_RESOLVES",
                            layer=ValidationLayer.SEMANTIC,
                            path=(collection, index, "evidence_ids", ref_index),
                            message=f"Unknown evidence id: {evidence_id}",
                        )
                    )
    return issues


def _release_semantic_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    sources = [item for item in payload.get("sources", []) if isinstance(item, dict)]
    artifacts = [item for item in payload.get("artifacts", []) if isinstance(item, dict)]
    derivations = [item for item in payload.get("derivations", []) if isinstance(item, dict)]

    source_ids = [
        item.get("source_id")
        for item in sources
        if isinstance(item.get("source_id"), str)
    ]
    artifact_ids = [
        item.get("artifact_id") for item in artifacts if isinstance(item.get("artifact_id"), str)
    ]

    if len(source_ids) != len(set(source_ids)):
        issues.append(
            ValidationIssue(
                "RELEASE_SOURCE_IDS_UNIQUE",
                ValidationLayer.SEMANTIC,
                ("sources",),
                "Source ids must be unique within a release manifest.",
            )
        )
    if len(artifact_ids) != len(set(artifact_ids)):
        issues.append(
            ValidationIssue(
                "RELEASE_ARTIFACT_IDS_UNIQUE",
                ValidationLayer.SEMANTIC,
                ("artifacts",),
                "Artifact ids must be unique within a release manifest.",
            )
        )

    source_by_id = {
        item["source_id"]: item for item in sources if isinstance(item.get("source_id"), str)
    }
    artifact_by_id = {
        item["artifact_id"]: item
        for item in artifacts
        if isinstance(item.get("artifact_id"), str)
    }

    for index, artifact in enumerate(artifacts):
        source_id = artifact.get("source_id")
        source = source_by_id.get(source_id)
        if source is None and isinstance(source_id, str):
            issues.append(
                ValidationIssue(
                    "RELEASE_ARTIFACT_SOURCE_RESOLVES",
                    ValidationLayer.SEMANTIC,
                    ("artifacts", index, "source_id"),
                    f"Unknown source id: {source_id}",
                )
            )
            continue

        if source is not None:
            snapshot = source.get("snapshot")
            snapshot_version = snapshot.get("version") if isinstance(snapshot, dict) else None
            artifact_version = artifact.get("source_version")
            if (
                artifact_version is not None
                and snapshot_version is not None
                and artifact_version != snapshot_version
            ):
                issues.append(
                    ValidationIssue(
                        "RELEASE_SOURCE_VERSION_MATCH",
                        ValidationLayer.SEMANTIC,
                        ("artifacts", index, "source_version"),
                        "Artifact source_version does not match source snapshot version.",
                    )
                )

    episode_ids: list[str] = []
    release_schema_version = payload.get("schema_version")
    for derivation_index, derivation in enumerate(derivations):
        artifact_id = derivation.get("source_artifact_id")
        artifact = artifact_by_id.get(artifact_id)
        if artifact is None and isinstance(artifact_id, str):
            issues.append(
                ValidationIssue(
                    "RELEASE_DERIVATION_ARTIFACT_RESOLVES",
                    ValidationLayer.SEMANTIC,
                    ("derivations", derivation_index, "source_artifact_id"),
                    f"Unknown artifact id: {artifact_id}",
                )
            )
        elif artifact is not None:
            if derivation.get("source_record_id") != artifact.get("record_id"):
                issues.append(
                    ValidationIssue(
                        "RELEASE_RECORD_LINEAGE_MATCH",
                        ValidationLayer.SEMANTIC,
                        ("derivations", derivation_index, "source_record_id"),
                        "Derivation source_record_id does not match its source artifact.",
                    )
                )

        for episode_index, episode in enumerate(derivation.get("episodes", [])):
            if not isinstance(episode, dict):
                continue
            episode_id = episode.get("episode_id")
            if isinstance(episode_id, str):
                episode_ids.append(episode_id)
            if episode.get("schema_version") != release_schema_version:
                issues.append(
                    ValidationIssue(
                        "RELEASE_EPISODE_SCHEMA_MATCH",
                        ValidationLayer.SEMANTIC,
                        (
                            "derivations",
                            derivation_index,
                            "episodes",
                            episode_index,
                            "schema_version",
                        ),
                        "Episode schema_version does not match release manifest schema_version.",
                    )
                )

    if len(episode_ids) != len(set(episode_ids)):
        issues.append(
            ValidationIssue(
                "RELEASE_EPISODE_IDS_UNIQUE",
                ValidationLayer.SEMANTIC,
                ("derivations",),
                "Episode ids must be unique across release derivations.",
            )
        )

    episode_count = payload.get("episode_count")
    if isinstance(episode_count, int) and episode_count != len(episode_ids):
        issues.append(
            ValidationIssue(
                "RELEASE_EPISODE_COUNT_MATCH",
                ValidationLayer.SEMANTIC,
                ("episode_count",),
                "episode_count must equal normalized episode references.",
            )
        )

    return issues


def validate_intervention_episode(payload: JSONValue) -> ValidationReport:
    structural = _structural_issues(payload, strict_intervention_episode_schema())
    semantic = _episode_semantic_issues(payload) if isinstance(payload, dict) else []
    return ValidationReport(
        ContractKind.INTERVENTION_EPISODE,
        "0.1.0",
        VALIDATION_PROFILE_VERSION,
        tuple([*structural, *semantic]),
    )


def validate_source_manifest(payload: JSONValue) -> ValidationReport:
    structural = _structural_issues(payload, strict_source_manifest_schema())
    return ValidationReport(
        ContractKind.SOURCE_MANIFEST,
        "0.1.0",
        VALIDATION_PROFILE_VERSION,
        tuple(structural),
    )


def validate_data_release_manifest(payload: JSONValue) -> ValidationReport:
    structural = _structural_issues(payload, strict_data_release_manifest_schema())
    semantic = _release_semantic_issues(payload) if isinstance(payload, dict) else []
    return ValidationReport(
        ContractKind.DATA_RELEASE_MANIFEST,
        "0.1.0",
        VALIDATION_PROFILE_VERSION,
        tuple([*structural, *semantic]),
    )
