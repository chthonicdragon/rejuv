from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from rejuv.releases import (
    AdapterSnapshot,
    DataReleaseManifest,
    DerivationRecord,
    fingerprint_episode,
    normalized_episode_ref,
)
from rejuv.sources import Checksum, SourceAdapter
from tests.support.synthetic_adapter import SyntheticAdapter


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "source_adapter" / "synthetic_source.json"


def run_synthetic_pipeline() -> tuple[SyntheticAdapter, object, list]:
    adapter = SyntheticAdapter(FIXTURE)
    record = next(iter(adapter.discover()))
    artifact = adapter.fetch(record)
    parsed = list(adapter.parse(artifact))
    episodes = [episode for item in parsed for episode in adapter.normalize(item)]
    adapter.validate(episodes)
    return adapter, artifact, episodes


def test_source_adapter_is_runtime_checkable() -> None:
    adapter = SyntheticAdapter(FIXTURE)
    assert isinstance(adapter, SourceAdapter)


def test_fetched_artifact_verifies_content_identity() -> None:
    _, artifact, _ = run_synthetic_pipeline()

    artifact.verify()
    assert artifact.metadata.size_bytes == len(artifact.content)
    assert artifact.metadata.checksum == Checksum.from_bytes(artifact.content)


def test_changed_raw_bytes_change_checksum() -> None:
    content = FIXTURE.read_bytes()
    changed = content.replace(b"no_change", b"increase")

    assert Checksum.from_bytes(content) != Checksum.from_bytes(changed)


def test_raw_to_normalized_derivation_is_deterministic() -> None:
    _, first_artifact, first_episodes = run_synthetic_pipeline()
    _, second_artifact, second_episodes = run_synthetic_pipeline()

    assert first_artifact.metadata.checksum == second_artifact.metadata.checksum
    assert [fingerprint_episode(item) for item in first_episodes] == [
        fingerprint_episode(item) for item in second_episodes
    ]


def test_release_manifest_captures_complete_lineage() -> None:
    adapter, artifact, episodes = run_synthetic_pipeline()
    episode = episodes[0]

    manifest = DataReleaseManifest(
        release_id="rejuv:release:synthetic-001",
        release_version="2026.09-test",
        created_at=datetime(2026, 9, 26, tzinfo=UTC),
        software_version="0.1.0",
        code_commit="0000000",
        sources=[adapter.source_manifest()],
        artifacts=[artifact.metadata],
        derivations=[
            DerivationRecord(
                derivation_id="rejuv:derivation:synthetic-001",
                source_artifact_id=artifact.metadata.artifact_id,
                source_record_id=episode.provenance.source_record_id or "",
                adapter=AdapterSnapshot(
                    adapter_id=adapter.adapter_id,
                    adapter_version=adapter.adapter_version,
                ),
                transformations=episode.provenance.transformations,
                episodes=[normalized_episode_ref(episode)],
            )
        ],
        episode_count=1,
    )

    assert manifest.episode_count == 1
    assert manifest.derivations[0].episodes[0].checksum == fingerprint_episode(episode)


def test_release_manifest_rejects_unknown_artifact_reference() -> None:
    adapter, artifact, episodes = run_synthetic_pipeline()
    episode = episodes[0]

    with pytest.raises(ValidationError, match="unknown artifact"):
        DataReleaseManifest(
            release_id="rejuv:release:broken",
            release_version="2026.09-test",
            created_at=datetime(2026, 9, 26, tzinfo=UTC),
            software_version="0.1.0",
            code_commit="0000000",
            sources=[adapter.source_manifest()],
            artifacts=[artifact.metadata],
            derivations=[
                DerivationRecord(
                    derivation_id="rejuv:derivation:broken",
                    source_artifact_id="missing-artifact",
                    source_record_id=episode.provenance.source_record_id or "",
                    adapter=AdapterSnapshot(
                        adapter_id=adapter.adapter_id,
                        adapter_version=adapter.adapter_version,
                    ),
                    episodes=[normalized_episode_ref(episode)],
                )
            ],
            episode_count=1,
        )
