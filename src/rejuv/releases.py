from __future__ import annotations

import json
from typing import Any, Final

from rejuv.contracts.v0_1_0.releases import (
    AdapterSnapshot,
    DataReleaseManifest,
    DerivationRecord,
    NormalizedEpisodeRef,
    OntologySnapshot,
)
from rejuv.models import CURRENT_SCHEMA_VERSION, InterventionEpisode
from rejuv.sources import Checksum


RELEASE_MANIFEST_VERSION: Final[str] = "0.1.0"
SUPPORTED_RELEASE_MANIFEST_VERSIONS: Final[tuple[str, ...]] = ("0.1.0",)


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


def normalized_episode_ref(episode: InterventionEpisode) -> NormalizedEpisodeRef:
    if episode.schema_version != CURRENT_SCHEMA_VERSION:
        raise ValueError(
            "normalized_episode_ref accepts only the current writer schema version."
        )
    return NormalizedEpisodeRef(
        episode_id=episode.episode_id,
        schema_version=episode.schema_version,
        checksum=fingerprint_episode(episode),
    )


__all__ = [
    "AdapterSnapshot",
    "DataReleaseManifest",
    "DerivationRecord",
    "NormalizedEpisodeRef",
    "OntologySnapshot",
    "RELEASE_MANIFEST_VERSION",
    "SUPPORTED_RELEASE_MANIFEST_VERSIONS",
    "canonical_json_bytes",
    "fingerprint_episode",
    "normalized_episode_ref",
]
