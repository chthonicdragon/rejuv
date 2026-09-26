from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from typing import Generic, Iterable, Protocol, Sequence, TypeVar, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from rejuv.models import InterventionEpisode


class SourceModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PermissionStatus(StrEnum):
    ALLOWED = "allowed"
    PROHIBITED = "prohibited"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


class Checksum(SourceModel):
    algorithm: str = "sha256"
    digest: str = Field(min_length=64, max_length=64)

    @field_validator("algorithm")
    @classmethod
    def only_sha256_for_v0_1(cls, value: str) -> str:
        if value != "sha256":
            raise ValueError("Source contract 0.1 supports only sha256 checksums.")
        return value

    @field_validator("digest")
    @classmethod
    def validate_digest(cls, value: str) -> str:
        normalized = value.lower()
        if any(char not in "0123456789abcdef" for char in normalized):
            raise ValueError("Checksum digest must be lowercase-compatible hexadecimal.")
        return normalized

    @classmethod
    def from_bytes(cls, content: bytes) -> "Checksum":
        return cls(digest=hashlib.sha256(content).hexdigest())

    def matches(self, content: bytes) -> bool:
        actual = hashlib.sha256(content).hexdigest()
        return hmac.compare_digest(self.digest, actual)


class UsagePolicy(SourceModel):
    redistribution: PermissionStatus = PermissionStatus.UNKNOWN
    derivative_data: PermissionStatus = PermissionStatus.UNKNOWN
    commercial_use: PermissionStatus = PermissionStatus.UNKNOWN
    model_training: PermissionStatus = PermissionStatus.UNKNOWN
    attribution_required: bool | None = None
    notes: str | None = None


class LicenseInfo(SourceModel):
    name: str = Field(min_length=1)
    spdx_id: str | None = None
    url: HttpUrl | None = None
    usage: UsagePolicy = Field(default_factory=UsagePolicy)
    citation: str | None = None


class SourceSnapshot(SourceModel):
    version: str | None = None
    released_at: date | None = None
    accessed_at: datetime
    etag: str | None = None
    last_modified: str | None = None
    immutable: bool = False


class SourceManifest(SourceModel):
    manifest_version: str = "0.1.0"
    source_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    homepage: HttpUrl | None = None
    snapshot: SourceSnapshot
    license: LicenseInfo
    update_cadence: str | None = None
    notes: str | None = None

    @field_validator("manifest_version")
    @classmethod
    def validate_manifest_version(cls, value: str) -> str:
        if value != "0.1.0":
            raise ValueError("Unsupported SourceManifest version.")
        return value


class SourceRecordRef(SourceModel):
    source_id: str = Field(min_length=1)
    record_id: str = Field(min_length=1)
    locator: str = Field(min_length=1)


class SourceArtifact(SourceModel):
    artifact_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    record_id: str = Field(min_length=1)
    locator: str = Field(min_length=1)
    checksum: Checksum
    size_bytes: int = Field(ge=0)
    media_type: str | None = None
    retrieved_at: datetime
    source_version: str | None = None


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
        retrieved_at: datetime,
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
class SourceAdapter(Protocol, Generic[ParsedT]):
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
