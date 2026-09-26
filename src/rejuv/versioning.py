from __future__ import annotations

from collections import deque
from collections.abc import Callable, Mapping
from copy import deepcopy
from enum import StrEnum
from typing import Any, cast

from pydantic import BaseModel

from rejuv.contracts.v0_1_0.models import InterventionEpisode as InterventionEpisodeV010
from rejuv.contracts.v0_1_0.releases import DataReleaseManifest as DataReleaseManifestV010
from rejuv.contracts.v0_1_0.sources import SourceManifest as SourceManifestV010
from rejuv.models import CURRENT_SCHEMA_VERSION
from rejuv.releases import RELEASE_MANIFEST_VERSION
from rejuv.sources import SOURCE_CONTRACT_VERSION


type JSONMapping = Mapping[str, Any]
type Migration = Callable[[dict[str, Any]], dict[str, Any]]
type InterventionEpisodeRecord = InterventionEpisodeV010
type SourceManifestRecord = SourceManifestV010
type DataReleaseManifestRecord = DataReleaseManifestV010


class ContractKind(StrEnum):
    INTERVENTION_EPISODE = "intervention_episode"
    SOURCE_MANIFEST = "source_manifest"
    DATA_RELEASE_MANIFEST = "data_release_manifest"


class UnsupportedContractVersionError(ValueError):
    pass


class MigrationNotAvailableError(ValueError):
    pass


_EPISODE_READERS: dict[str, type[BaseModel]] = {
    "0.1.0": InterventionEpisodeV010,
}
_SOURCE_MANIFEST_READERS: dict[str, type[BaseModel]] = {
    "0.1.0": SourceManifestV010,
}
_RELEASE_MANIFEST_READERS: dict[str, type[BaseModel]] = {
    "0.1.0": DataReleaseManifestV010,
}

# Trusted migrations are code-owned. Third-party adapters/plugins must not be able to
# register runtime transformations that reinterpret historical scientific records.
# Add migration edges here together with the target contract version and tests.
_MIGRATIONS: dict[ContractKind, dict[tuple[str, str], Migration]] = {
    ContractKind.INTERVENTION_EPISODE: {},
    ContractKind.SOURCE_MANIFEST: {},
    ContractKind.DATA_RELEASE_MANIFEST: {},
}


SUPPORTED_INTERVENTION_SCHEMA_VERSIONS = tuple(_EPISODE_READERS)
SUPPORTED_SOURCE_MANIFEST_VERSIONS = tuple(_SOURCE_MANIFEST_READERS)
SUPPORTED_RELEASE_MANIFEST_VERSIONS = tuple(_RELEASE_MANIFEST_READERS)


def _readers_for(kind: ContractKind) -> Mapping[str, type[BaseModel]]:
    if kind is ContractKind.INTERVENTION_EPISODE:
        return _EPISODE_READERS
    if kind is ContractKind.SOURCE_MANIFEST:
        return _SOURCE_MANIFEST_READERS
    if kind is ContractKind.DATA_RELEASE_MANIFEST:
        return _RELEASE_MANIFEST_READERS
    raise AssertionError(f"Unhandled contract kind: {kind}")


def _version_field_for(kind: ContractKind) -> str:
    if kind is ContractKind.INTERVENTION_EPISODE:
        return "schema_version"
    return "manifest_version"


def _payload_copy(payload: JSONMapping) -> dict[str, Any]:
    return deepcopy(dict(payload))


def _required_version(payload: JSONMapping, field: str, kind: ContractKind) -> str:
    version = payload.get(field)
    if not isinstance(version, str) or not version:
        raise UnsupportedContractVersionError(
            f"{kind.value} requires a non-empty {field!r} string."
        )
    return version


def _load(
    payload: JSONMapping,
    *,
    kind: ContractKind,
    version_field: str,
    readers: Mapping[str, type[BaseModel]],
) -> BaseModel:
    version = _required_version(payload, version_field, kind)
    reader = readers.get(version)
    if reader is None:
        supported = ", ".join(readers) or "none"
        raise UnsupportedContractVersionError(
            f"Unsupported {kind.value} version {version!r}; supported read versions: "
            f"{supported}."
        )
    return reader.model_validate(_payload_copy(payload))


def load_intervention_episode(payload: JSONMapping) -> InterventionEpisodeRecord:
    return cast(
        InterventionEpisodeRecord,
        _load(
            payload,
            kind=ContractKind.INTERVENTION_EPISODE,
            version_field="schema_version",
            readers=_EPISODE_READERS,
        ),
    )


def load_source_manifest(payload: JSONMapping) -> SourceManifestRecord:
    return cast(
        SourceManifestRecord,
        _load(
            payload,
            kind=ContractKind.SOURCE_MANIFEST,
            version_field="manifest_version",
            readers=_SOURCE_MANIFEST_READERS,
        ),
    )


def load_data_release_manifest(payload: JSONMapping) -> DataReleaseManifestRecord:
    return cast(
        DataReleaseManifestRecord,
        _load(
            payload,
            kind=ContractKind.DATA_RELEASE_MANIFEST,
            version_field="manifest_version",
            readers=_RELEASE_MANIFEST_READERS,
        ),
    )


def current_version(kind: ContractKind) -> str:
    if kind is ContractKind.INTERVENTION_EPISODE:
        return CURRENT_SCHEMA_VERSION
    if kind is ContractKind.SOURCE_MANIFEST:
        return SOURCE_CONTRACT_VERSION
    if kind is ContractKind.DATA_RELEASE_MANIFEST:
        return RELEASE_MANIFEST_VERSION
    raise AssertionError(f"Unhandled contract kind: {kind}")


def _find_migration_path(
    kind: ContractKind,
    from_version: str,
    to_version: str,
) -> list[tuple[str, str]]:
    if from_version == to_version:
        return []

    edges = _MIGRATIONS[kind]
    queue: deque[tuple[str, list[tuple[str, str]]]] = deque([(from_version, [])])
    visited = {from_version}

    while queue:
        version, path = queue.popleft()
        for edge in edges:
            source, target = edge
            if source != version or target in visited:
                continue

            next_path = [*path, edge]
            if target == to_version:
                return next_path

            visited.add(target)
            queue.append((target, next_path))

    raise MigrationNotAvailableError(
        f"No migration path for {kind.value}: {from_version} -> {to_version}."
    )


def migrate_payload(
    kind: ContractKind,
    payload: JSONMapping,
    *,
    target_version: str | None = None,
) -> dict[str, Any]:
    version_field = _version_field_for(kind)
    readers = _readers_for(kind)
    source_version = _required_version(payload, version_field, kind)
    source_reader = readers.get(source_version)
    if source_reader is None:
        supported = ", ".join(readers) or "none"
        raise UnsupportedContractVersionError(
            f"Cannot migrate unsupported {kind.value} version {source_version!r}; "
            f"supported read versions: {supported}."
        )

    # Migration starts from a payload that is valid under its historical contract.
    source_reader.model_validate(_payload_copy(payload))

    target = target_version or current_version(kind)
    result = _payload_copy(payload)

    for edge in _find_migration_path(kind, source_version, target):
        result = _MIGRATIONS[kind][edge](_payload_copy(result))
        actual = _required_version(result, version_field, kind)
        if actual != edge[1]:
            raise ValueError(
                f"Migration {kind.value} {edge[0]} -> {edge[1]} returned "
                f"version {actual!r}."
            )

        target_reader = readers.get(actual)
        if target_reader is None:
            raise UnsupportedContractVersionError(
                f"Migration target {kind.value} version {actual!r} has no registered reader."
            )
        target_reader.model_validate(_payload_copy(result))

    return result


def migrate_intervention_episode(
    payload: JSONMapping,
    *,
    target_version: str = CURRENT_SCHEMA_VERSION,
) -> dict[str, Any]:
    return migrate_payload(
        ContractKind.INTERVENTION_EPISODE,
        payload,
        target_version=target_version,
    )


def migrate_source_manifest(
    payload: JSONMapping,
    *,
    target_version: str = SOURCE_CONTRACT_VERSION,
) -> dict[str, Any]:
    return migrate_payload(
        ContractKind.SOURCE_MANIFEST,
        payload,
        target_version=target_version,
    )


def migrate_data_release_manifest(
    payload: JSONMapping,
    *,
    target_version: str = RELEASE_MANIFEST_VERSION,
) -> dict[str, Any]:
    return migrate_payload(
        ContractKind.DATA_RELEASE_MANIFEST,
        payload,
        target_version=target_version,
    )
