# RFC-0001: InterventionEpisode v0.1

- **Status:** Accepted for initial implementation
- **Schema target:** 0.1.0
- **Scope:** core biological intervention representation

## Summary

Adopt `InterventionEpisode` as the canonical unit of Rejuv.

An episode represents:

```text
biological context
+ baseline observations
+ ordered intervention sequence
+ elapsed time
-> outcomes / adverse effects
+ evidence / provenance
```

## Motivation

Most biological datasets are optimized for storage around papers, samples, assays, genes, or compounds.

AI-driven experimental science instead needs an action-centered representation:

```text
STATE + ACTION + TIME -> NEXT STATE
```

The schema should support static prediction today and sequential experiment planning later without changing the fundamental abstraction.

## Goals

The initial protocol must support:

- multiple organisms;
- tissue/cell context;
- one or more ordered interventions;
- dose and timing;
- baseline measurements;
- post-intervention outcomes;
- adverse outcomes;
- evidence references;
- provenance;
- uncertainty;
- external ontology identifiers.

## Non-goals

v0.1 does not attempt to fully model:

- complete molecular state;
- clinical treatment plans;
- pharmacokinetic simulation;
- causal graphs;
- whole-organism digital twins;
- every experimental design;
- every unit system.

Extensions should be evidence-driven.

## Decisions

### D1. Episode, not paper, is canonical

A paper can yield many episodes.

### D2. Intervention sequence is ordered

Even a single intervention is represented as a one-element ordered sequence.

This avoids a breaking redesign when sequence benchmarks arrive.

### D3. Context is explicit

Organism, tissue, and cell type belong to biological context rather than being encoded into free-text labels.

### D4. External ontology references

Ontology references use generic `id + label + namespace` structures so Rejuv can interoperate without becoming an ontology.

### D5. Values disclose origin

Measurements/outcomes distinguish measured, author-reported, derived, inferred, and model-generated values.

### D6. Timing is explicit

Offsets and durations use a numeric value plus time unit in v0.1.

### D7. Provenance is mandatory at episode level

An episode without at least one evidence reference is invalid for production data. Synthetic fixtures may use a clearly marked synthetic evidence reference.

## Candidate shape

```json
{
  "episode_id": "rejuv:episode:...",
  "schema_version": "0.1.0",
  "study_id": "rejuv:study:...",
  "context": {
    "organism": {"id": "NCBITaxon:9606", "label": "Homo sapiens"},
    "tissue": {"id": "UBERON:0000178", "label": "blood"}
  },
  "baseline": [],
  "interventions": [
    {
      "order": 1,
      "type": "compound",
      "agent": {"id": "CHEBI:...", "label": "..."},
      "start": {"value": 0, "unit": "day"}
    }
  ],
  "follow_up": {"value": 30, "unit": "day"},
  "outcomes": [],
  "adverse_effects": [],
  "evidence": [],
  "provenance": {
    "curation_level": "L1"
  }
}
```

## Compatibility

Before 1.0, schema evolution follows semantic versioning:

- patch: constraints/docs that do not alter valid record meaning;
- minor: backward-compatible fields or enum additions;
- major: breaking semantic/structural changes.

## Open questions

Tracked for later RFCs:

- unit ontology and conversion policy;
- explicit comparator-arm representation;
- subject-level vs aggregate episodes;
- probabilistic outcomes;
- composite interventions;
- causal assumptions;
- confidential partner evidence.

## Acceptance criteria

RFC-0001 is implemented when:

1. Pydantic models validate the core shape;
2. generated JSON Schema is checked in;
3. a synthetic example validates;
4. tests verify key invalid states;
5. docs explain evidence and missingness rules.
