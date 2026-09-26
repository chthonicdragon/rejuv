from __future__ import annotations

from enum import StrEnum
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


CURRENT_SCHEMA_VERSION: Final[str] = "0.1.0"
SUPPORTED_SCHEMA_VERSIONS: Final[tuple[str, ...]] = ("0.1.0",)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TimeUnit(StrEnum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class ValueOrigin(StrEnum):
    MEASURED = "measured"
    AUTHOR_REPORTED = "author_reported"
    DERIVED = "derived"
    INFERRED = "inferred"
    MODEL_GENERATED = "model_generated"


class CurationLevel(StrEnum):
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class InterventionType(StrEnum):
    COMPOUND = "compound"
    GENE_KNOCKOUT = "gene_knockout"
    GENE_SUPPRESSION = "gene_suppression"
    GENE_ACTIVATION = "gene_activation"
    RNA = "rna"
    GENOME_EDITING = "genome_editing"
    EPIGENOME_EDITING = "epigenome_editing"
    PARTIAL_REPROGRAMMING = "partial_reprogramming"
    CELL_THERAPY = "cell_therapy"
    DIETARY = "dietary"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"


class OutcomeCategory(StrEnum):
    MOLECULAR = "molecular"
    CELLULAR = "cellular"
    FUNCTIONAL = "functional"
    HEALTHSPAN = "healthspan"
    LIFESPAN = "lifespan"
    PATHOLOGY = "pathology"
    SAFETY = "safety"


class EffectDirection(StrEnum):
    INCREASE = "increase"
    DECREASE = "decrease"
    NO_CHANGE = "no_change"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class OntologyRef(StrictModel):
    id: str = Field(min_length=1, description="Persistent external or Rejuv identifier.")
    label: str | None = None
    namespace: str | None = None
    uri: HttpUrl | None = None


class Quantity(StrictModel):
    value: float
    unit: str = Field(min_length=1)


class TimeOffset(StrictModel):
    value: float = Field(ge=0)
    unit: TimeUnit


class EvidenceReference(StrictModel):
    evidence_id: str = Field(min_length=1)
    source_type: Literal[
        "paper",
        "dataset",
        "repository",
        "supplement",
        "database",
        "synthetic",
    ]
    doi: str | None = None
    pmid: str | None = None
    accession: str | None = None
    url: HttpUrl | None = None
    locator: str | None = None
    note: str | None = None

    @model_validator(mode="after")
    def require_source_pointer(self) -> "EvidenceReference":
        if self.source_type == "synthetic":
            return self
        if not any((self.doi, self.pmid, self.accession, self.url)):
            raise ValueError(
                "Non-synthetic evidence requires at least one DOI, PMID, accession, or URL."
            )
        return self


class BiologicalContext(StrictModel):
    organism: OntologyRef
    tissue: OntologyRef | None = None
    cell_type: OntologyRef | None = None
    sex: Literal[
        "female",
        "male",
        "mixed",
        "not_reported",
        "not_applicable",
        "other",
    ] | None = None
    chronological_age: Quantity | None = None
    disease_states: list[OntologyRef] = Field(default_factory=list)
    genotype: str | None = None
    subject_id: str | None = None
    notes: str | None = None


ScalarValue = float | int | str | bool


class Measurement(StrictModel):
    measurement_id: str | None = None
    name: str = Field(min_length=1)
    ontology_term: OntologyRef | None = None
    modality: str | None = None
    value: ScalarValue | None = None
    unit: str | None = None
    time: TimeOffset | None = None
    origin: ValueOrigin
    uncertainty: float | None = Field(default=None, ge=0)
    evidence_ids: list[str] = Field(default_factory=list)


class Intervention(StrictModel):
    intervention_id: str = Field(min_length=1)
    order: int = Field(ge=1)
    type: InterventionType
    agent: OntologyRef | None = None
    target: OntologyRef | None = None
    dose: Quantity | None = None
    route: str | None = None
    start: TimeOffset = Field(default_factory=lambda: TimeOffset(value=0, unit=TimeUnit.DAY))
    duration: TimeOffset | None = None
    protocol_text: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class Outcome(StrictModel):
    outcome_id: str = Field(min_length=1)
    category: OutcomeCategory
    name: str = Field(min_length=1)
    ontology_term: OntologyRef | None = None
    value: ScalarValue | None = None
    unit: str | None = None
    effect_direction: EffectDirection = EffectDirection.UNKNOWN
    comparator: str | None = None
    time: TimeOffset | None = None
    origin: ValueOrigin
    uncertainty: float | None = Field(default=None, ge=0)
    evidence_ids: list[str] = Field(default_factory=list)


class AdverseEffect(StrictModel):
    adverse_effect_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    severity: Literal["mild", "moderate", "severe", "fatal", "unknown"] = "unknown"
    serious: bool | None = None
    value: ScalarValue | None = None
    unit: str | None = None
    time: TimeOffset | None = None
    origin: ValueOrigin
    evidence_ids: list[str] = Field(default_factory=list)


class Provenance(StrictModel):
    curation_level: CurationLevel
    source_record_id: str | None = None
    adapter: str | None = None
    adapter_version: str | None = None
    extraction_method: Literal["manual", "rule_based", "ai_assisted", "imported"] | None = None
    extraction_model: str | None = None
    transformations: list[str] = Field(default_factory=list)
    reviewers: list[str] = Field(default_factory=list)
    notes: str | None = None


class InterventionEpisode(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "x-rejuv-schema-version": CURRENT_SCHEMA_VERSION,
            "x-rejuv-supported-schema-versions": list(SUPPORTED_SCHEMA_VERSIONS),
        },
    )

    episode_id: str = Field(min_length=1)
    schema_version: Literal["0.1.0"] = "0.1.0"
    study_id: str = Field(min_length=1)
    context: BiologicalContext
    baseline: list[Measurement] = Field(default_factory=list)
    interventions: list[Intervention] = Field(min_length=1)
    follow_up: TimeOffset | None = None
    outcomes: list[Outcome] = Field(default_factory=list)
    adverse_effects: list[AdverseEffect] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(min_length=1)
    provenance: Provenance

    @model_validator(mode="after")
    def validate_intervention_order(self) -> "InterventionEpisode":
        orders = [item.order for item in self.interventions]
        if len(orders) != len(set(orders)):
            raise ValueError("Intervention order values must be unique.")
        if orders != sorted(orders):
            raise ValueError("Interventions must be serialized in ascending order.")
        return self

    @model_validator(mode="after")
    def validate_evidence_links(self) -> "InterventionEpisode":
        known = {item.evidence_id for item in self.evidence}
        referenced: set[str] = set()

        for measurement in self.baseline:
            referenced.update(measurement.evidence_ids)
        for intervention in self.interventions:
            referenced.update(intervention.evidence_ids)
        for outcome in self.outcomes:
            referenced.update(outcome.evidence_ids)
        for effect in self.adverse_effects:
            referenced.update(effect.evidence_ids)

        missing = sorted(referenced - known)
        if missing:
            raise ValueError(f"Unknown evidence_ids referenced: {missing}")
        return self


def intervention_episode_json_schema() -> dict[str, Any]:
    """Return the generated JSON Schema for the current InterventionEpisode model."""
    return InterventionEpisode.model_json_schema()
