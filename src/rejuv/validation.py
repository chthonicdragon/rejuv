from __future__ import annotations

from typing import Any, Final, Protocol

from rejuv.validation_profiles import v0_1_0
from rejuv.validation_types import (
    JSONValue,
    UnsupportedValidationProfileError,
    ValidationIssue,
    ValidationLayer,
    ValidationReport,
)


VALIDATION_PROFILE_VERSION: Final[str] = "0.1.0"
SUPPORTED_VALIDATION_PROFILE_VERSIONS: Final[tuple[str, ...]] = ("0.1.0",)


class _ValidationProfile(Protocol):
    def validation_profile(self) -> dict[str, Any]: ...

    def strict_intervention_episode_schema(self) -> dict[str, Any]: ...

    def strict_source_manifest_schema(self) -> dict[str, Any]: ...

    def strict_data_release_manifest_schema(self) -> dict[str, Any]: ...

    def validate_intervention_episode(self, payload: JSONValue) -> ValidationReport: ...

    def validate_source_manifest(self, payload: JSONValue) -> ValidationReport: ...

    def validate_data_release_manifest(self, payload: JSONValue) -> ValidationReport: ...


_PROFILES: dict[str, _ValidationProfile] = {
    "0.1.0": v0_1_0,
}


def _profile(profile_version: str) -> _ValidationProfile:
    profile = _PROFILES.get(profile_version)
    if profile is None:
        supported = ", ".join(SUPPORTED_VALIDATION_PROFILE_VERSIONS)
        raise UnsupportedValidationProfileError(
            f"Unsupported validation profile {profile_version!r}; supported: {supported}."
        )
    return profile


def validation_profile(
    profile_version: str = VALIDATION_PROFILE_VERSION,
) -> dict[str, Any]:
    return _profile(profile_version).validation_profile()


def strict_intervention_episode_schema(
    profile_version: str = VALIDATION_PROFILE_VERSION,
) -> dict[str, Any]:
    return _profile(profile_version).strict_intervention_episode_schema()


def strict_source_manifest_schema(
    profile_version: str = VALIDATION_PROFILE_VERSION,
) -> dict[str, Any]:
    return _profile(profile_version).strict_source_manifest_schema()


def strict_data_release_manifest_schema(
    profile_version: str = VALIDATION_PROFILE_VERSION,
) -> dict[str, Any]:
    return _profile(profile_version).strict_data_release_manifest_schema()


def validate_intervention_episode(
    payload: JSONValue,
    *,
    profile_version: str = VALIDATION_PROFILE_VERSION,
) -> ValidationReport:
    return _profile(profile_version).validate_intervention_episode(payload)


def validate_source_manifest(
    payload: JSONValue,
    *,
    profile_version: str = VALIDATION_PROFILE_VERSION,
) -> ValidationReport:
    return _profile(profile_version).validate_source_manifest(payload)


def validate_data_release_manifest(
    payload: JSONValue,
    *,
    profile_version: str = VALIDATION_PROFILE_VERSION,
) -> ValidationReport:
    return _profile(profile_version).validate_data_release_manifest(payload)


__all__ = [
    "SUPPORTED_VALIDATION_PROFILE_VERSIONS",
    "UnsupportedValidationProfileError",
    "VALIDATION_PROFILE_VERSION",
    "ValidationIssue",
    "ValidationLayer",
    "ValidationReport",
    "strict_data_release_manifest_schema",
    "strict_intervention_episode_schema",
    "strict_source_manifest_schema",
    "validate_data_release_manifest",
    "validate_intervention_episode",
    "validate_source_manifest",
    "validation_profile",
]
