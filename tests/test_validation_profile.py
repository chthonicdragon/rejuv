from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from rejuv.models import InterventionEpisode
from rejuv.releases import DataReleaseManifest
from rejuv.sources import SourceManifest
from rejuv.validation import (
    VALIDATION_PROFILE_VERSION,
    UnsupportedValidationProfileError,
    strict_data_release_manifest_schema,
    strict_intervention_episode_schema,
    strict_source_manifest_schema,
    validate_data_release_manifest,
    validate_intervention_episode,
    validate_source_manifest,
    validation_profile,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "validation_0_1_0"
EXAMPLES = ROOT / "examples"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def load_example(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def test_strict_schemas_are_valid_draft_2020_12() -> None:
    for schema in (
        strict_intervention_episode_schema(),
        strict_source_manifest_schema(),
        strict_data_release_manifest_schema(),
    ):
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["x-rejuv-validation-profile-version"] == VALIDATION_PROFILE_VERSION
        Draft202012Validator.check_schema(schema)


def test_validation_profile_has_unique_stable_rule_ids() -> None:
    profile = validation_profile()
    assert profile["profile_version"] == VALIDATION_PROFILE_VERSION
    rule_ids = [rule["rule_id"] for rule in profile["rules"]]
    assert len(rule_ids) == len(set(rule_ids))


def test_unknown_validation_profile_fails_explicitly() -> None:
    with pytest.raises(UnsupportedValidationProfileError, match="Unsupported"):
        validation_profile("9.9.9")


def test_validation_report_is_machine_serializable() -> None:
    report = validate_intervention_episode(load_example("intervention_episode.synthetic.json"))
    payload = report.as_dict()

    assert payload["valid"] is True
    assert payload["structural_valid"] is True
    assert payload["semantic_valid"] is True
    assert payload["validation_profile_version"] == VALIDATION_PROFILE_VERSION


def test_missing_evidence_pointer_fails_portable_and_semantic_validation() -> None:
    payload = load_fixture("episode_missing_evidence_pointer.json")
    report = validate_intervention_episode(payload)

    assert not report.structural_valid
    assert not report.semantic_valid
    assert "EVIDENCE_SOURCE_POINTER_REQUIRED" in issue_codes(report)
    with pytest.raises(ValidationError):
        InterventionEpisode.model_validate(payload)


def test_duplicate_intervention_order_is_semantic_not_structural() -> None:
    payload = load_fixture("episode_duplicate_order.json")
    report = validate_intervention_episode(payload)

    assert report.structural_valid
    assert not report.semantic_valid
    assert "INTERVENTION_ORDER_UNIQUE" in issue_codes(report)
    with pytest.raises(ValidationError):
        InterventionEpisode.model_validate(payload)


def test_unsorted_intervention_order_is_semantic_not_structural() -> None:
    payload = load_fixture("episode_unsorted_order.json")
    report = validate_intervention_episode(payload)

    assert report.structural_valid
    assert not report.semantic_valid
    assert "INTERVENTION_ORDER_ASCENDING" in issue_codes(report)
    with pytest.raises(ValidationError):
        InterventionEpisode.model_validate(payload)


def test_unknown_evidence_reference_is_semantic_not_structural() -> None:
    payload = load_fixture("episode_unknown_evidence.json")
    report = validate_intervention_episode(payload)

    assert report.structural_valid
    assert not report.semantic_valid
    assert "EVIDENCE_REFERENCE_RESOLVES" in issue_codes(report)
    with pytest.raises(ValidationError):
        InterventionEpisode.model_validate(payload)


def test_release_unknown_artifact_is_semantic_not_structural() -> None:
    payload = load_fixture("release_unknown_artifact.json")
    report = validate_data_release_manifest(payload)

    assert report.structural_valid
    assert not report.semantic_valid
    assert "RELEASE_DERIVATION_ARTIFACT_RESOLVES" in issue_codes(report)
    with pytest.raises(ValidationError):
        DataReleaseManifest.model_validate(payload)


def test_bad_checksum_is_rejected_by_portable_schema_and_pydantic() -> None:
    payload = load_fixture("release_bad_checksum.json")
    report = validate_data_release_manifest(payload)

    assert not report.structural_valid
    with pytest.raises(ValidationError):
        DataReleaseManifest.model_validate(payload)


def test_http_url_constraint_is_portable() -> None:
    payload = load_fixture("source_invalid_http_url.json")
    report = validate_source_manifest(payload)

    assert not report.structural_valid
    with pytest.raises(ValidationError):
        SourceManifest.model_validate(payload)


@pytest.mark.parametrize(
    ("code", "mutator"),
    [
        (
            "RELEASE_SOURCE_IDS_UNIQUE",
            lambda payload: payload["sources"].append(deepcopy(payload["sources"][0])),
        ),
        (
            "RELEASE_ARTIFACT_IDS_UNIQUE",
            lambda payload: payload["artifacts"].append(deepcopy(payload["artifacts"][0])),
        ),
        (
            "RELEASE_ARTIFACT_SOURCE_RESOLVES",
            lambda payload: payload["artifacts"][0].update(source_id="missing-source"),
        ),
        (
            "RELEASE_SOURCE_VERSION_MATCH",
            lambda payload: payload["artifacts"][0].update(source_version="wrong-version"),
        ),
        (
            "RELEASE_RECORD_LINEAGE_MATCH",
            lambda payload: payload["derivations"][0].update(source_record_id="wrong-record"),
        ),
        (
            "RELEASE_EPISODE_SCHEMA_MATCH",
            lambda payload: payload["derivations"][0]["episodes"][0].update(
                schema_version="0.2.0"
            ),
        ),
        (
            "RELEASE_EPISODE_COUNT_MATCH",
            lambda payload: payload.update(episode_count=99),
        ),
    ],
)
def test_release_semantic_rules_match_pydantic_rejection(code, mutator) -> None:
    payload = load_example("data_release_manifest.synthetic.json")
    mutator(payload)
    report = validate_data_release_manifest(payload)

    assert code in issue_codes(report)
    assert not report.semantic_valid
    with pytest.raises(ValidationError):
        DataReleaseManifest.model_validate(payload)


def test_duplicate_episode_ids_match_pydantic_rejection() -> None:
    payload = load_example("data_release_manifest.synthetic.json")
    second = deepcopy(payload["derivations"][0])
    second["derivation_id"] = "rejuv:derivation:synthetic-002"
    payload["derivations"].append(second)
    payload["episode_count"] = 2

    report = validate_data_release_manifest(payload)

    assert "RELEASE_EPISODE_IDS_UNIQUE" in issue_codes(report)
    assert not report.semantic_valid
    with pytest.raises(ValidationError):
        DataReleaseManifest.model_validate(payload)


def test_semantic_validation_does_not_crash_on_malformed_structures() -> None:
    release_report = validate_data_release_manifest(
        {
            "sources": [{"source_id": []}],
            "artifacts": [{"source_id": [], "artifact_id": []}],
            "derivations": [{"source_artifact_id": [], "episodes": {}}],
            "episode_count": 0,
        }
    )
    episode_report = validate_intervention_episode(
        {
            "interventions": {"not": "an array"},
            "evidence": {"not": "an array"},
            "outcomes": [{"evidence_ids": {"not": "an array"}}],
        }
    )

    assert not release_report.structural_valid
    assert not episode_report.structural_valid
