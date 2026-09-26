from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from rejuv.models import (
    CURRENT_SCHEMA_VERSION,
    InterventionEpisode,
    intervention_episode_json_schema,
)
from rejuv.releases import DataReleaseManifest
from rejuv.sources import SourceManifest
import scripts.check_schema_contract as schema_contract

from rejuv.validation import (
    VALIDATION_PROFILE_VERSION,
    strict_data_release_manifest_schema,
    strict_intervention_episode_schema,
    strict_source_manifest_schema,
    validation_profile,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = ROOT / "examples" / "intervention_episode.synthetic.json"
COMPAT_FIXTURE_PATH = (
    ROOT / "tests" / "fixtures" / "schema_0_1_0" / "intervention_episode.minimal.json"
)
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

ARTIFACTS: dict[Path, dict[str, Any]] = {
    Path("schemas/intervention_episode.schema.json"): intervention_episode_json_schema(),
    Path("schemas/source_manifest.schema.json"): SourceManifest.model_json_schema(),
    Path("schemas/data_release_manifest.schema.json"): DataReleaseManifest.model_json_schema(),
    Path("schemas/validation/v0_1_0/intervention_episode.schema.json"): (
        strict_intervention_episode_schema()
    ),
    Path("schemas/validation/v0_1_0/source_manifest.schema.json"): (
        strict_source_manifest_schema()
    ),
    Path("schemas/validation/v0_1_0/data_release_manifest.schema.json"): (
        strict_data_release_manifest_schema()
    ),
    Path("schemas/validation/v0_1_0/profile.json"): validation_profile(),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("relative_path", ARTIFACTS)
def test_checked_in_artifact_matches_generator(relative_path: Path) -> None:
    assert load_json(ROOT / relative_path) == ARTIFACTS[relative_path]


@pytest.mark.parametrize(
    "relative_path",
    [path for path in ARTIFACTS if path.name.endswith(".schema.json")],
)
def test_exported_schema_is_valid_draft_2020_12(relative_path: Path) -> None:
    schema = load_json(ROOT / relative_path)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_schema_and_validation_profile_versions_are_semver() -> None:
    schema = load_json(ROOT / "schemas" / "intervention_episode.schema.json")
    schema_version = schema["x-rejuv-schema-version"]

    assert schema_version == CURRENT_SCHEMA_VERSION
    assert SEMVER_RE.fullmatch(schema_version)
    assert SEMVER_RE.fullmatch(VALIDATION_PROFILE_VERSION)


def test_strict_schema_declares_validation_profile() -> None:
    for relative_path in (
        Path("schemas/validation/v0_1_0/intervention_episode.schema.json"),
        Path("schemas/validation/v0_1_0/source_manifest.schema.json"),
        Path("schemas/validation/v0_1_0/data_release_manifest.schema.json"),
    ):
        schema = load_json(ROOT / relative_path)
        assert schema["x-rejuv-validation-profile-version"] == VALIDATION_PROFILE_VERSION


def test_public_example_remains_compatible_with_record_schema() -> None:
    payload = load_json(EXAMPLE_PATH)
    InterventionEpisode.model_validate(payload)
    schema = load_json(ROOT / "schemas" / "intervention_episode.schema.json")
    Draft202012Validator(schema).validate(payload)


def test_0_1_0_compatibility_fixture_remains_valid() -> None:
    """Protect the first public record shape before schema 0.2.0 exists."""
    payload = load_json(COMPAT_FIXTURE_PATH)

    assert payload["schema_version"] == "0.1.0"
    InterventionEpisode.model_validate(payload)
    schema = load_json(ROOT / "schemas" / "intervention_episode.schema.json")
    Draft202012Validator(schema).validate(payload)


def test_validation_profile_artifact_paths_follow_profile_version() -> None:
    profile_dir = "v" + VALIDATION_PROFILE_VERSION.replace(".", "_")
    expected_prefix = Path("schemas") / "validation" / profile_dir

    profile_paths = [
        path for path in ARTIFACTS if path.parts[:2] == ("schemas", "validation")
    ]
    assert profile_paths
    assert all(path.parent == expected_prefix for path in profile_paths)


def test_new_validation_profile_has_no_frozen_base_conflict(monkeypatch) -> None:
    monkeypatch.setattr(schema_contract, "load_base_schema", lambda path: None)
    assert schema_contract.check_validation_profile_immutability() == []


def test_frozen_validation_profile_rejects_same_version_changes(monkeypatch) -> None:
    def fake_base(path: Path):
        current = schema_contract.load_json(schema_contract.ROOT / path)
        if path.name == "profile.json":
            changed = dict(current)
            changed["profile_version"] = "tampered-same-version"
            return changed
        return current

    monkeypatch.setattr(schema_contract, "load_base_schema", fake_base)
    errors = schema_contract.check_validation_profile_immutability()

    assert len(errors) == 1
    assert "Frozen validation profile artifact changed" in errors[0]
