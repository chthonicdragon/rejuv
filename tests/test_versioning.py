from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from rejuv.contracts.v0_1_0.models import InterventionEpisode as InterventionEpisodeV010
from rejuv.contracts.v0_1_0.releases import (
    DataReleaseManifest as DataReleaseManifestV010,
)
from rejuv.contracts.v0_1_0.sources import SourceManifest as SourceManifestV010
from rejuv.models import CURRENT_SCHEMA_VERSION, InterventionEpisode
from rejuv.releases import DataReleaseManifest, RELEASE_MANIFEST_VERSION
from rejuv.sources import SOURCE_CONTRACT_VERSION, SourceManifest
from rejuv.versioning import (
    ContractKind,
    MigrationNotAvailableError,
    UnsupportedContractVersionError,
    load_data_release_manifest,
    load_intervention_episode,
    load_source_manifest,
    migrate_intervention_episode,
    migrate_payload,
    register_migration,
)


ROOT = Path(__file__).resolve().parents[1]
EPISODE_FIXTURE = ROOT / "tests" / "fixtures" / "schema_0_1_0" / "intervention_episode.minimal.json"
SOURCE_FIXTURE = ROOT / "tests" / "fixtures" / "contracts_0_1_0" / "source_manifest.json"
RELEASE_FIXTURE = ROOT / "tests" / "fixtures" / "contracts_0_1_0" / "data_release_manifest.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_current_writer_aliases_point_to_versioned_0_1_contracts() -> None:
    assert CURRENT_SCHEMA_VERSION == "0.1.0"
    assert SOURCE_CONTRACT_VERSION == "0.1.0"
    assert RELEASE_MANIFEST_VERSION == "0.1.0"

    assert InterventionEpisode is InterventionEpisodeV010
    assert SourceManifest is SourceManifestV010
    assert DataReleaseManifest is DataReleaseManifestV010


def test_versioned_loaders_read_frozen_0_1_contracts_without_mutating_payload() -> None:
    episode_payload = load_json(EPISODE_FIXTURE)
    source_payload = load_json(SOURCE_FIXTURE)
    release_payload = load_json(RELEASE_FIXTURE)

    originals = (
        deepcopy(episode_payload),
        deepcopy(source_payload),
        deepcopy(release_payload),
    )

    episode = load_intervention_episode(episode_payload)
    source = load_source_manifest(source_payload)
    release = load_data_release_manifest(release_payload)

    assert type(episode) is InterventionEpisodeV010
    assert type(source) is SourceManifestV010
    assert type(release) is DataReleaseManifestV010

    assert episode_payload == originals[0]
    assert source_payload == originals[1]
    assert release_payload == originals[2]


@pytest.mark.parametrize(
    ("loader", "payload", "version_field"),
    [
        (
            load_intervention_episode,
            {"schema_version": "9.9.9"},
            "schema_version",
        ),
        (
            load_source_manifest,
            {"manifest_version": "9.9.9"},
            "manifest_version",
        ),
        (
            load_data_release_manifest,
            {"manifest_version": "9.9.9"},
            "manifest_version",
        ),
    ],
)
def test_unknown_contract_versions_fail_explicitly(loader, payload, version_field) -> None:
    with pytest.raises(UnsupportedContractVersionError, match="Unsupported"):
        loader(payload)

    with pytest.raises(UnsupportedContractVersionError, match=version_field):
        loader({})


def test_same_version_migration_is_a_non_mutating_copy() -> None:
    payload = load_json(EPISODE_FIXTURE)
    migrated = migrate_intervention_episode(payload)

    assert migrated == payload
    assert migrated is not payload

    migrated["episode_id"] = "changed"
    assert payload["episode_id"] != "changed"


def test_missing_migration_path_fails_instead_of_guessing() -> None:
    payload = load_json(EPISODE_FIXTURE)

    with pytest.raises(MigrationNotAvailableError, match="0.1.0 -> 0.2.0"):
        migrate_intervention_episode(payload, target_version="0.2.0")


def test_explicit_migration_registry_supports_future_chains() -> None:
    def to_test_020(payload: dict) -> dict:
        payload["schema_version"] = "test-0.2.0"
        payload["migration_marker"] = "first"
        return payload

    def to_test_030(payload: dict) -> dict:
        payload["schema_version"] = "test-0.3.0"
        payload["migration_marker"] += "-second"
        return payload

    register_migration(
        ContractKind.INTERVENTION_EPISODE,
        "0.1.0",
        "test-0.2.0",
        to_test_020,
    )
    register_migration(
        ContractKind.INTERVENTION_EPISODE,
        "test-0.2.0",
        "test-0.3.0",
        to_test_030,
    )

    original = load_json(EPISODE_FIXTURE)
    migrated = migrate_payload(
        ContractKind.INTERVENTION_EPISODE,
        original,
        target_version="test-0.3.0",
    )

    assert migrated["schema_version"] == "test-0.3.0"
    assert migrated["migration_marker"] == "first-second"
    assert original["schema_version"] == "0.1.0"
    assert "migration_marker" not in original
