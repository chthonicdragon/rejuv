# RFC-0004: Structural and semantic validation profiles

- **Status:** Accepted for initial implementation
- **Validation profile:** 0.1.0
- **Record contracts:** InterventionEpisode 0.1.0, SourceManifest 0.1.0, DataReleaseManifest 0.1.0

## Summary

Rejuv defines record format and record validity as related but distinct contracts.

Official validation is two-stage:

```text
serialized payload
      |
      v
strict JSON Schema (structural / portable)
      |
      v
semantic validation profile (cross-field / graph rules)
      |
      v
ValidationReport
```

The validation profile has its own version. Updating validation behavior does not by
itself change the serialized record schema version.

## Motivation

Pydantic 0.1 readers contain Python-only validators for evidence references, intervention
ordering, referential integrity, and release graph consistency. Generated JSON Schema
cannot express all of those rules. Pydantic can also coerce some input types, while a
JSON Schema implementation may reject them.

Therefore `Model.model_validate()` is a versioned Python reader/deserializer, not the
language-neutral definition of a valid Rejuv record.

## Decisions

### D1. Validation profiles are independently versioned

`schema_version` describes serialized data shape and meaning.

`validation_profile_version` describes the exact validation rules and portable schema
augmentations applied to that data.

A validation bug fix or improved portable constraint may bump the profile without
rewriting historical scientific records.

### D2. Strict JSON Schema is the portable structural layer

Rejuv exports Draft 2020-12 schemas for all public top-level contracts.

The strict schemas may add constraints omitted by Pydantic's generated schema when they
are safely expressible in JSON Schema, including:

- non-synthetic evidence source-pointer requirement;
- SHA-256 algorithm/digest syntax;
- HTTP/HTTPS URL scheme constraints matching `HttpUrl` intent.

### D3. Semantic rules have stable ids

Rules that require ordering, referential integrity, or graph traversal are evaluated by
the semantic engine and return stable machine-readable ids such as:

- `INTERVENTION_ORDER_UNIQUE`;
- `EVIDENCE_REFERENCE_RESOLVES`;
- `RELEASE_DERIVATION_ARTIFACT_RESOLVES`.

Messages are explanatory; automation should key on rule ids.

### D4. Critical portable rules may be checked twice

A rule such as `EVIDENCE_SOURCE_POINTER_REQUIRED` is expressible in JSON Schema and also
checked by the semantic engine so Python callers receive a stable semantic rule id.

This intentional overlap does not change validity: either layer may reject the record.

### D5. Semantic validation does not repair data

Validators report issues. They do not reorder interventions, create evidence links,
coerce identifiers, or infer missing values.

### D6. Frozen historical readers remain frozen

RFC-0004 does not modify `contracts/v0_1_0` to implement a new record version.

The validation layer operates beside historical readers. A reader answers:

> Can this payload be parsed under the historical Python contract?

The validation profile answers:

> Does this payload satisfy the portable and semantic validity contract?

### D7. Public schema artifacts are generated and drift-checked

Generated artifacts include:

```text
schemas/intervention_episode.schema.json
schemas/source_manifest.schema.json
schemas/data_release_manifest.schema.json
schemas/validation/v0_1_0/intervention_episode.schema.json
schemas/validation/v0_1_0/source_manifest.schema.json
schemas/validation/v0_1_0/data_release_manifest.schema.json
schemas/validation/v0_1_0/profile.json
```

Hand edits are prohibited.

## Rule classification

### Structural / JSON Schema

Examples:

- required fields;
- enums and literal versions;
- primitive types and array/object shape;
- numeric bounds;
- URL syntax/scheme;
- checksum syntax;
- non-synthetic evidence requires a public source pointer.

### Semantic

Examples:

- intervention order uniqueness and ordering;
- evidence references resolve;
- release ids are unique;
- artifact/source and derivation/artifact references resolve;
- release source versions and record lineage agree;
- episode ids/counts/schema versions agree with the release graph.

## Compatibility

Record schema 0.1.0 remains 0.1.0.

Validation profile 0.1.0 is the first explicit validation profile. Future profile changes
must document whether they fix an implementation gap or intentionally tighten validity.

## Non-goals

RFC-0004 does not define new biological fields, migrate old records, redesign artifact
topology (#11), or add experimental-design semantics (#12).

## Acceptance criteria

- all public top-level contracts have exported JSON Schema;
- strict schemas are Draft 2020-12 valid;
- semantic violations have stable rule ids and paths;
- negative fixtures prove structural-only and semantic-only failure modes;
- public examples pass both validation stages;
- generated artifacts are drift-checked;
- documentation states that Pydantic readers are not the language-neutral validity contract.
