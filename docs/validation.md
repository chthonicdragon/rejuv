# Validation

## The contract has two layers

A Rejuv record is valid only when it passes:

1. the strict JSON Schema for its contract/profile;
2. the semantic rules for that validation profile.

Use the public Python helpers:

```python
from rejuv import validate_intervention_episode

report = validate_intervention_episode(payload)
if not report.valid:
    for issue in report.issues:
        print(issue.code, issue.path, issue.message)
```

`ValidationReport.structural_valid` and `.semantic_valid` expose the two stages.

## Do not use Pydantic alone as the external validity definition

Historical Pydantic models remain authoritative readers for the Python implementation of
their serialized version, but they contain Python-only validators and may perform input
coercion.

For data interchange, ingestion, benchmarks, or agent APIs, use the validation profile.

## Versioning

These versions are independent:

```text
record schema             0.1.0
source manifest contract  0.1.0
release manifest contract 0.1.0
validation profile        0.1.0
```

A validation-profile update does not silently rewrite a record or change its
`schema_version`.

## Public invariants

| Invariant | Layer | Stable rule id / mechanism |
|---|---|---|
| Required fields/types/enums/bounds | structural | JSON Schema keywords |
| HTTP/HTTPS URL intent | structural | JSON Schema `format` + scheme pattern |
| Non-synthetic evidence has DOI/PMID/accession/URL | structural + semantic | `EVIDENCE_SOURCE_POINTER_REQUIRED` |
| Intervention order values are unique | semantic | `INTERVENTION_ORDER_UNIQUE` |
| Interventions serialized in ascending order | semantic | `INTERVENTION_ORDER_ASCENDING` |
| `evidence_ids` resolve | semantic | `EVIDENCE_REFERENCE_RESOLVES` |
| SHA-256 algorithm/digest syntax | structural | strict checksum schema |
| Release source ids unique | semantic | `RELEASE_SOURCE_IDS_UNIQUE` |
| Release artifact ids unique | semantic | `RELEASE_ARTIFACT_IDS_UNIQUE` |
| Artifact source resolves | semantic | `RELEASE_ARTIFACT_SOURCE_RESOLVES` |
| Artifact source version matches source snapshot | semantic | `RELEASE_SOURCE_VERSION_MATCH` |
| Derivation artifact resolves | semantic | `RELEASE_DERIVATION_ARTIFACT_RESOLVES` |
| Derivation record matches artifact record | semantic | `RELEASE_RECORD_LINEAGE_MATCH` |
| Episode-ref schema matches release schema | semantic | `RELEASE_EPISODE_SCHEMA_MATCH` |
| Episode ids unique across derivations | semantic | `RELEASE_EPISODE_IDS_UNIQUE` |
| Episode count matches references | semantic | `RELEASE_EPISODE_COUNT_MATCH` |

## Structural error codes

JSON Schema failures are reported as `JSON_SCHEMA_<KEYWORD>` (for example
`JSON_SCHEMA_REQUIRED` or `JSON_SCHEMA_PATTERN`) with the failing JSON path.

These codes identify the schema mechanism. Semantic automation should use the explicit
semantic rule ids listed above.

The machine-readable `profile.json` enumerates the non-trivial named invariants that
need stable cross-language identities. Ordinary field-level structural constraints
(required fields, primitive types, enums, bounds, and similar rules) remain fully
specified by the exported strict JSON Schemas rather than being duplicated as thousands
of profile rule entries.

## Generated artifacts

Run:

```bash
python scripts/export_schema.py
```

Do not hand-edit files under `schemas/`.

See [RFC-0004](../rfcs/0004-validation-profiles.md).
