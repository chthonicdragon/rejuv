# Schemas

Rejuv publishes two related kinds of machine-readable artifacts.

## Record schemas

These describe the serialized shape generated from the current writer contracts:

```text
schemas/intervention_episode.schema.json
schemas/source_manifest.schema.json
schemas/data_release_manifest.schema.json
```

They are generated, never hand-edited.

## Validation profiles

Record shape is not enough for scientific validity. Cross-field, ordering, referential,
and graph rules are versioned separately as validation profiles.

Profile 0.1.0 exports:

```text
schemas/validation/v0_1_0/intervention_episode.schema.json
schemas/validation/v0_1_0/source_manifest.schema.json
schemas/validation/v0_1_0/data_release_manifest.schema.json
schemas/validation/v0_1_0/profile.json
```

The strict schemas contain portable constraints that JSON Schema 2020-12 can express.
The profile describes semantic rules and their stable ids.

A record is considered valid for interchange only after both stages pass:

```text
strict JSON Schema
        +
semantic validation
        =
valid Rejuv payload
```

Do not treat a successful Pydantic `model_validate()` call as the language-neutral
validity contract. Historical Pydantic models are versioned readers/deserializers and
may contain Python-specific validation or coercion behavior.

## Generation

Run:

```bash
python scripts/export_schema.py
```

The command writes all public schema and validation artifacts.

`python scripts/check_schema_contract.py` fails if any checked-in generated artifact
drifts from code.

## Independent versioning

The following versions are intentionally separate:

```text
software version
record schema version
source-manifest contract version
release-manifest contract version
validation-profile version
data-release version
```

A validation-profile change does not silently rewrite historical scientific records.

## Historical contracts and profiles

Historical record readers are frozen under:

```text
src/rejuv/contracts/vX_Y_Z/
```

Historical validation profiles are frozen under:

```text
src/rejuv/validation_profiles/vX_Y_Z.py
```

Do not edit an old frozen contract/profile to implement a new version. Add a new version
and retain compatibility/parity fixtures.

See:

- [docs/versioning.md](../docs/versioning.md)
- [docs/validation.md](../docs/validation.md)
- [RFC-0003](../rfcs/0003-contract-versioning.md)
- [RFC-0004](../rfcs/0004-validation-profiles.md)
