from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Final, Protocol, TypeVar, runtime_checkable

from pydantic import AwareDatetime

from rejuv.contracts.v0_1_0.sources import (
    Checksum,
    LicenseInfo,
    PermissionStatus,
    SourceArtifact,
    SourceManifest,
    SourceModel,
    SourceRecordRef,
    SourceSnapshot,
    UsagePolicy,
)
from rejuv.models import InterventionEpisode


SOURCE_CONTRACT_VERSION: Final[str] = "0.1.0"
SUPPORTED_SOURCE_CONTRACT_VERSIONS: Final[tuple[str, ...]] = ("0.1.0",)


@dataclass(frozen=True, slots=True)
class FetchedArtifact:
    metadata: SourceArtifact
    content: bytes

    @classmethod
    def from_content(
        cls,
        *,
        artifact_id: str,
        record: SourceRecordRef,
        content: bytes,
        retrieved_at: AwareDatetime,
        media_type: str | None = None,
        source_version: str | None = None,
    ) -> "FetchedArtifact":
        metadata = SourceArtifact(
            artifact_id=artifact_id,
            source_id=record.source_id,
            record_id=record.record_id,
            locator=record.locator,
            checksum=Checksum.from_bytes(content),
            size_bytes=len(content),
            media_type=media_type,
            retrieved_at=retrieved_at,
            source_version=source_version,
        )
        return cls(metadata=metadata, content=content)

    def verify(self) -> None:
        if self.metadata.size_bytes != len(self.content):
            raise ValueError("Fetched artifact byte length does not match metadata.")
        if not self.metadata.checksum.matches(self.content):
            raise ValueError("Fetched artifact checksum does not match content.")


ParsedT = TypeVar("ParsedT")


@runtime_checkable
class SourceAdapter(Protocol[ParsedT]):
    adapter_id: str
    adapter_version: str

    def source_manifest(self) -> SourceManifest:
        """Describe the exact upstream source snapshot and its usage policy."""
        ...

    def discover(self) -> Iterable[SourceRecordRef]:
        """Yield stable references to source records without normalizing them."""
        ...

    def fetch(self, record: SourceRecordRef) -> FetchedArtifact:
        """Fetch one raw artifact and attach immutable content identity."""
        ...

    def parse(self, artifact: FetchedArtifact) -> Iterable[ParsedT]:
        """Parse source-specific raw content without changing biological meaning."""
        ...

    def normalize(self, record: ParsedT) -> Iterable[InterventionEpisode]:
        """Map one parsed source record into Rejuv episodes."""
        ...

    def validate(self, episodes: Sequence[InterventionEpisode]) -> None:
        """Run source-specific invariants; raise on invalid normalized output."""
        ...


__all__ = [
    "Checksum",
    "FetchedArtifact",
    "LicenseInfo",
    "PermissionStatus",
    "SOURCE_CONTRACT_VERSION",
    "SUPPORTED_SOURCE_CONTRACT_VERSIONS",
    "SourceAdapter",
    "SourceArtifact",
    "SourceManifest",
    "SourceModel",
    "SourceRecordRef",
    "SourceSnapshot",
    "UsagePolicy",
]
