from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import Field, model_validator

from rejuv.models import CURRENT_SCHEMA_VERSION, InterventionEpisode
from rejuv.sources import Checksum, SourceArtifact, SourceManifest, SourceModel


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def fingerprint_episode(episode: InterventionEpisode) -> Checksum:
    payload = episode.model_dump(mode="json", exclude_none=False)
    return Checksum.from_bytes(canonical_json_bytes(payload))


class AdapterSnapshot(SourceModel):
    adapter_id: str = Field(min_length=1)
    adapter_version: str = Field(min_length=1)


class OntologySnapshot(SourceModel):
    namespace: str = Field(min_length=1)
    version: str | None = None
    source_uri: str | None = None
    checksum: Checksum | None = None


class NormalizedEpisodeRef(SourceModel):
    episode_id: str = Field(min_length=1)
    schema_version: str = CURRENT_SCHEMA_VERSION
    checksum: Checksum


class DerivationRecord(SourceModel):
    derivation_id: str = Field(min_length=1)
    source_artifact_id: str = Field(min_length=1)
    source_record_id: str = Field(min_length=1)
    adapter: AdapterSnapshot
    transformations: list[str] = Field(default_factory=list)
    episodes: list[NormalizedEpisodeRef] = Field(min_length=1)


class DataReleaseManifest(SourceModel):
    manifest_version: str = "0.1.0"
    release_id: str = Field(min_length=1)
    release_version: str = Field(min_length=1)
    created_at: datetime
    schema_version: str = CURRENT_SCHEMA_VERSION
    software_version: str = Field(min_length=1)
    code_commit: str = Field(min_length=7)
    sources: list[SourceManifest] = Field(min_length=1)
    artifacts: list[SourceArtifact] = Field(default_factory=list)
    derivations: list[DerivationRecord] = Field(default_factory=list)
    ontology_snapshots: list[OntologySnapshot] = Field(default_factory=list)
    episode_count: int = Field(ge=0)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_graph(self) -> "DataReleaseManifest":
        source_ids = [source.source_id for source in self.sources]
        artifact_ids = [artifact.artifact_id for artifact in self.artifacts]

        if len(source_ids) != len(set(source_ids)):
            raise ValueError("Source ids must be unique within a release manifest.")
        if len(artifact_ids) != len(set(artifact_ids)):
            raise ValueError("Artifact ids must be unique within a release manifest.")

        known_sources = set(source_ids)
        for artifact in self.artifacts:
            if artifact.source_id not in known_sources:
                raise ValueError(
                    f"Artifact {artifact.artifact_id!r} references unknown source "
                    f"{artifact.source_id!r}."
                )

        known_artifacts = set(artifact_ids)
        episode_ids: list[str] = []
        for derivation in self.derivations:
            if derivation.source_artifact_id not in known_artifacts:
                raise ValueError(
                    f"Derivation {derivation.derivation_id!r} references unknown artifact "
                    f"{derivation.source_artifact_id!r}."
                )
            episode_ids.extend(item.episode_id for item in derivation.episodes)

        if len(episode_ids) != len(set(episode_ids)):
            raise ValueError("Episode ids must be unique across release derivations.")

        if self.episode_count != len(episode_ids):
            raise ValueError(
                "episode_count must equal the number of normalized episode references."
            )

        if self.schema_version != CURRENT_SCHEMA_VERSION:
            raise ValueError(
                "Release manifest schema_version must match the current Rejuv schema."
            )

        return self


def normalized_episode_ref(episode: InterventionEpisode) -> NormalizedEpisodeRef:
    return NormalizedEpisodeRef(
        episode_id=episode.episode_id,
        schema_version=episode.schema_version,
        checksum=fingerprint_episode(episode),
    )
