from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from rejuv.models import (
    CURRENT_SCHEMA_VERSION,
    InterventionEpisode,
    intervention_episode_json_schema,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "intervention_episode.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "intervention_episode.synthetic.json"
COMPAT_FIXTURE_PATH = (
    ROOT / "tests" / "fixtures" / "schema_0_1_0" / "intervention_episode.minimal.json"
)
SEMVER_RE = re.compile(r"^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_checked_in_schema_matches_pydantic_source_of_truth() -> None:
    assert load_json(SCHEMA_PATH) == intervention_episode_json_schema()


def test_generated_schema_is_valid_draft_2020_12() -> None:
    schema = load_json(SCHEMA_PATH)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_schema_version_is_semver_and_matches_model_contract() -> None:
    schema = load_json(SCHEMA_PATH)
    version = schema["x-rejuv-schema-version"]

    assert version == CURRENT_SCHEMA_VERSION
    assert SEMVER_RE.fullmatch(version)

    # Versioning contract from RFC-0001:
    # - patch: no semantic change to valid records;
    # - minor: backward-compatible schema capability;
    # - major: breaking schema semantics.
    #
    # CI also compares the PR schema with the base branch. Any schema artifact
    # change requires a monotonically increased schema version.


def test_public_example_validates_with_pydantic_and_json_schema() -> None:
    payload = load_json(EXAMPLE_PATH)
    InterventionEpisode.model_validate(payload)
    Draft202012Validator(load_json(SCHEMA_PATH)).validate(payload)


def test_0_1_0_compatibility_fixture_remains_valid() -> None:
    """Protect the first public record shape before schema 0.2.0 exists."""
    payload = load_json(COMPAT_FIXTURE_PATH)

    assert payload["schema_version"] == "0.1.0"
    InterventionEpisode.model_validate(payload)
    Draft202012Validator(load_json(SCHEMA_PATH)).validate(payload)
