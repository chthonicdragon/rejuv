# Schemas

Rejuv uses a single-source-of-truth policy for schema behavior.

During pre-1.0 development, the authoritative implementation is the typed Pydantic model in:

```text
src/rejuv/models.py
```

The language-neutral JSON Schema artifact is generated with:

```bash
python scripts/export_schema.py
```

The generated artifact is committed at:

```text
schemas/intervention_episode.schema.json
```

Do not hand-edit it.

## Reproducibility

Schema generation is part of the public contract. The development environment pins the Pydantic generator version used by CI so a dependency upgrade cannot silently rewrite the checked-in schema.

CI performs two independent checks:

1. the checked-in JSON Schema must equal the schema generated from the current Pydantic model;
2. on pull requests, if the generated schema differs from the base branch, `schema_version` must increase monotonically.

## Versioning

Schema versions are independent from software and data releases.

```text
software: 0.x.y
schema:   0.x.y
data:     YYYY.MM
```

RFC-0001 currently defines:

- patch: constraints/docs that do not change the semantics of valid records;
- minor: backward-compatible schema capability;
- major: breaking schema semantics.

A breaking semantic change also requires an RFC and migration notes.

Compatibility fixtures under `tests/fixtures/schema_<version>/` protect previously published record shapes. Do not delete an old fixture simply to make a new schema pass.

## Historical readers

The checked-in schema file represents the **current writer** contract.

Historical Python readers are frozen under `src/rejuv/contracts/vX_Y_Z/` and selected
through `rejuv.versioning`.

Do not validate stored historical records by assuming the current writer version.
See [docs/versioning.md](../docs/versioning.md) and RFC-0003.
