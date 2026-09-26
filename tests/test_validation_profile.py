from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from rejuv.models import InterventionEpisode
from rejuv.releases import DataReleaseManifest
from rejuv.sources import SourceManifest
from rejuv.validation import (
    VALIDATION_PROFILE_VERSION,
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


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


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


def test_missing_evidence_pointer_fails_portable_and_semantic_validation() -> None:
    payload = load("episode_missing_evidence_pointer.json")
    report = validate_intervention_episode(payload)

    assert not report.structural_valid
    assert not report.semantic_valid
    assert "EVIDENCE_SOURCE_POINTER_REQUIRED" in issue_codes(report)
    with pytest.raises(ValidationError):
        InterventionEpisode.model_validate(payload)


def test_duplicate_intervention_order_is_semantic_not_structural() -> None:
    payload = load("episode_duplicate_order.json")
    report = validate_intervention_episode(payload)

    assert report.structural_valid
    assert not report.semantic_valid
    assert "INTERVENTION_ORDER_UNIQUE" in issue_codes(report)
    with pytest.raises(ValidationError):
        InterventionEpisode.model_validate(payload)


def test_unknown_evidence_reference_is_semantic_not_structural() -> None:
    payload = load("episode_unknown_evidence.json")
    report = validate_intervention_episode(payload)

    assert report.structural_valid
    assert not report.semantic_valid
    assert "EVIDENCE_REFERENCE_RESOLVES" in issue_codes(report)
    with pytest.raises(ValidationError):
        InterventionEpisode.model_validate(payload)


def test_release_unknown_artifact_is_semantic_not_structural() -> None:
    payload = load("release_unknown_artifact.json")
    report = validate_data_release_manifest(payload)

    assert report.structural_valid
    assert not report.semantic_valid
    assert "RELEASE_DERIVATION_ARTIFACT_RESOLVES" in issue_codes(report)
    with pytest.raises(ValidationError):
        DataReleaseManifest.model_validate(payload)


def test_bad_checksum_is_rejected_by_portable_schema_and_pydantic() -> None:
    payload = load("release_bad_checksum.json")
    report = validate_data_release_manifest(payload)

    assert not report.structural_valid
    with pytest.raises(ValidationError):
        DataReleaseManifest.model_validate(payload)


def test_http_url_constraint_is_portable() -> None:
    payload = load("source_invalid_http_url.json")
    report = validate_source_manifest(payload)

    assert not report.structural_valid
    with pytest.raises(ValidationError):
        SourceManifest.model_validate(payload)
