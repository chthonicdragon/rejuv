from __future__ import annotations

import hashlib
import hmac
from datetime import date
from enum import StrEnum
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, HttpUrl, field_validator


SOURCE_CONTRACT_VERSION = "0.1.0"


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
    accessed_at: AwareDatetime
    etag: str | None = None
    last_modified: str | None = None
    immutable: bool = False


class SourceManifest(SourceModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "x-rejuv-source-contract-version": SOURCE_CONTRACT_VERSION,
        },
    )

    manifest_version: Literal["0.1.0"] = "0.1.0"
    source_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    homepage: HttpUrl | None = None
    snapshot: SourceSnapshot
    license: LicenseInfo
    update_cadence: str | None = None
    notes: str | None = None


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
    retrieved_at: AwareDatetime
    source_version: str | None = None
