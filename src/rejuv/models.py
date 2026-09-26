from __future__ import annotations

from typing import Any, Final

from rejuv.contracts.v0_1_0.models import (
    AdverseEffect,
    BiologicalContext,
    CurationLevel,
    EffectDirection,
    EvidenceReference,
    Intervention,
    InterventionEpisode,
    InterventionType,
    Measurement,
    OntologyRef,
    Outcome,
    OutcomeCategory,
    Provenance,
    Quantity,
    ScalarValue,
    StrictModel,
    TimeOffset,
    TimeUnit,
    ValueOrigin,
)


CURRENT_SCHEMA_VERSION: Final[str] = "0.1.0"
SUPPORTED_SCHEMA_VERSIONS: Final[tuple[str, ...]] = ("0.1.0",)


def intervention_episode_json_schema() -> dict[str, Any]:
    """Return JSON Schema for the current writer contract."""
    return InterventionEpisode.model_json_schema()


__all__ = [
    "AdverseEffect",
    "BiologicalContext",
    "CURRENT_SCHEMA_VERSION",
    "CurationLevel",
    "EffectDirection",
    "EvidenceReference",
    "Intervention",
    "InterventionEpisode",
    "InterventionType",
    "Measurement",
    "OntologyRef",
    "Outcome",
    "OutcomeCategory",
    "Provenance",
    "Quantity",
    "SUPPORTED_SCHEMA_VERSIONS",
    "ScalarValue",
    "StrictModel",
    "TimeOffset",
    "TimeUnit",
    "ValueOrigin",
    "intervention_episode_json_schema",
]
