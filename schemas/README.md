# Schemas

Rejuv uses a single-source-of-truth policy for schema behavior.

During pre-1.0 development, the authoritative implementation is the typed Pydantic model in:

```text
src/rejuv/models.py
```

Language-neutral JSON Schema artifacts are generated with:

```bash
python scripts/export_schema.py
```

Generated schemas will be committed once the first schema-consistency check is enabled. Do not hand-edit generated JSON Schema files.

## Versioning

Schema versions are independent from software and data releases.

```text
software: 0.x.y
schema:   0.x.y
data:     YYYY.MM
```

Breaking schema semantics require an RFC.
