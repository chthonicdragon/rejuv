from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from rejuv.versioning import ContractKind


type JSONValue = dict[str, Any] | list[Any] | str | int | float | bool | None
type PathPart = str | int


class ValidationLayer(StrEnum):
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    layer: ValidationLayer
    path: tuple[PathPart, ...]
    message: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "layer": self.layer.value,
            "path": list(self.path),
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    contract_kind: ContractKind
    contract_version: str
    validation_profile_version: str
    issues: tuple[ValidationIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues

    @property
    def structural_valid(self) -> bool:
        return not any(issue.layer is ValidationLayer.STRUCTURAL for issue in self.issues)

    @property
    def semantic_valid(self) -> bool:
        return not any(issue.layer is ValidationLayer.SEMANTIC for issue in self.issues)

    def as_dict(self) -> dict[str, Any]:
        return {
            "contract_kind": self.contract_kind.value,
            "contract_version": self.contract_version,
            "validation_profile_version": self.validation_profile_version,
            "valid": self.valid,
            "structural_valid": self.structural_valid,
            "semantic_valid": self.semantic_valid,
            "issues": [issue.as_dict() for issue in self.issues],
        }


class UnsupportedValidationProfileError(ValueError):
    pass
