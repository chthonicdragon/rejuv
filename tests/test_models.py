import pytest
from pydantic import ValidationError

from rejuv.models import InterventionEpisode


def synthetic_episode() -> dict:
    return {
        "episode_id": "rejuv:episode:test-1",
        "schema_version": "0.1.0",
        "study_id": "rejuv:study:test-1",
        "context": {
            "organism": {
                "id": "NCBITaxon:9606",
                "label": "Homo sapiens",
                "namespace": "NCBITaxon",
            }
        },
        "baseline": [],
        "interventions": [
            {
                "intervention_id": "rejuv:intervention:test-1",
                "order": 1,
                "type": "partial_reprogramming",
                "start": {"value": 0, "unit": "day"},
                "evidence_ids": ["rejuv:evidence:test-1"],
            }
        ],
        "follow_up": {"value": 30, "unit": "day"},
        "outcomes": [
            {
                "outcome_id": "rejuv:outcome:test-1",
                "category": "molecular",
                "name": "synthetic example outcome",
                "effect_direction": "unknown",
                "origin": "model_generated",
                "evidence_ids": ["rejuv:evidence:test-1"],
            }
        ],
        "adverse_effects": [],
        "evidence": [
            {
                "evidence_id": "rejuv:evidence:test-1",
                "source_type": "synthetic",
                "note": "Synthetic fixture; not scientific evidence.",
            }
        ],
        "provenance": {
            "curation_level": "L0",
            "extraction_method": "manual",
        },
    }


def test_valid_synthetic_episode() -> None:
    episode = InterventionEpisode.model_validate(synthetic_episode())
    assert episode.schema_version == "0.1.0"
    assert episode.interventions[0].order == 1


def test_unknown_evidence_reference_fails() -> None:
    payload = synthetic_episode()
    payload["outcomes"][0]["evidence_ids"] = ["rejuv:evidence:missing"]

    with pytest.raises(ValidationError, match="Unknown evidence_ids"):
        InterventionEpisode.model_validate(payload)


def test_duplicate_intervention_order_fails() -> None:
    payload = synthetic_episode()
    second = dict(payload["interventions"][0])
    second["intervention_id"] = "rejuv:intervention:test-2"
    payload["interventions"].append(second)

    with pytest.raises(ValidationError, match="order values must be unique"):
        InterventionEpisode.model_validate(payload)
