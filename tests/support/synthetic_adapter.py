from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

from rejuv.models import (
    BiologicalContext,
    CurationLevel,
    EffectDirection,
    EvidenceReference,
    Intervention,
    InterventionEpisode,
    InterventionType,
    OntologyRef,
    Outcome,
    OutcomeCategory,
    Provenance,
    ValueOrigin,
)
from rejuv.sources import (
    FetchedArtifact,
    LicenseInfo,
    PermissionStatus,
    SourceAdapter,
    SourceManifest,
    SourceRecordRef,
    SourceSnapshot,
    UsagePolicy,
)


class SyntheticAdapter(SourceAdapter[dict[str, Any]]):
    adapter_id = "rejuv.synthetic"
    adapter_version = "0.1.0"

    def __init__(self, fixture_path: Path) -> None:
        self.fixture_path = fixture_path

    def source_manifest(self) -> SourceManifest:
        return SourceManifest(
            source_id="synthetic-source",
            name="Synthetic Rejuv Source",
            owner="Rejuv tests",
            snapshot=SourceSnapshot(
                version="fixture-1",
                accessed_at=datetime(2026, 9, 26, tzinfo=UTC),
                immutable=True,
            ),
            license=LicenseInfo(
                name="Synthetic fixture",
                spdx_id="CC0-1.0",
                usage=UsagePolicy(
                    redistribution=PermissionStatus.ALLOWED,
                    derivative_data=PermissionStatus.ALLOWED,
                    commercial_use=PermissionStatus.ALLOWED,
                    model_training=PermissionStatus.ALLOWED,
                    attribution_required=False,
                ),
            ),
        )

    def discover(self) -> Iterable[SourceRecordRef]:
        payload = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        for record in payload["records"]:
            yield SourceRecordRef(
                source_id="synthetic-source",
                record_id=record["record_id"],
                locator=f"fixture://{record['record_id']}",
            )

    def fetch(self, record: SourceRecordRef) -> FetchedArtifact:
        content = self.fixture_path.read_bytes()
        return FetchedArtifact.from_content(
            artifact_id=f"synthetic-artifact:{record.record_id}",
            record=record,
            content=content,
            retrieved_at=datetime(2026, 9, 26, tzinfo=UTC),
            media_type="application/json",
            source_version="fixture-1",
        )

    def parse(self, artifact: FetchedArtifact) -> Iterable[dict[str, Any]]:
        artifact.verify()
        payload = json.loads(artifact.content)
        for record in payload["records"]:
            if record["record_id"] == artifact.metadata.record_id:
                yield record

    def normalize(self, record: dict[str, Any]) -> Iterable[InterventionEpisode]:
        evidence_id = f"rejuv:evidence:{record['record_id']}"
        episode = InterventionEpisode(
            episode_id=f"rejuv:episode:{record['record_id']}",
            study_id="rejuv:study:synthetic-adapter",
            context=BiologicalContext(
                organism=OntologyRef(
                    id=record["organism_id"],
                    label=record["organism_label"],
                    namespace="NCBITaxon",
                )
            ),
            interventions=[
                Intervention(
                    intervention_id=f"rejuv:intervention:{record['record_id']}",
                    order=1,
                    type=InterventionType(record["intervention_type"]),
                    evidence_ids=[evidence_id],
                )
            ],
            outcomes=[
                Outcome(
                    outcome_id=f"rejuv:outcome:{record['record_id']}",
                    category=OutcomeCategory.FUNCTIONAL,
                    name=record["outcome_name"],
                    effect_direction=EffectDirection(record["effect_direction"]),
                    origin=ValueOrigin.AUTHOR_REPORTED,
                    evidence_ids=[evidence_id],
                )
            ],
            evidence=[
                EvidenceReference(
                    evidence_id=evidence_id,
                    source_type="synthetic",
                    note="Synthetic adapter fixture; not scientific evidence.",
                )
            ],
            provenance=Provenance(
                curation_level=CurationLevel.L1,
                source_record_id=record["record_id"],
                adapter=self.adapter_id,
                adapter_version=self.adapter_version,
                extraction_method="imported",
                transformations=["synthetic-normalization-v1"],
            ),
        )
        yield episode

    def validate(self, episodes: Sequence[InterventionEpisode]) -> None:
        if not episodes:
            raise ValueError("Synthetic adapter must emit at least one episode.")

        for episode in episodes:
            if episode.provenance.adapter != self.adapter_id:
                raise ValueError("Episode provenance does not identify this adapter.")
