# RFC-0003: Contract versioning, historical readers, and explicit migration

- **Status:** Accepted for initial implementation
- **Scope:** InterventionEpisode, SourceManifest, DataReleaseManifest
- **Initial historical version:** 0.1.0

## Summary

Rejuv separates three concerns that must not be conflated:

1. **current writer** — the contract used to create new records;
2. **historical reader** — the frozen validator for the version a record was authored in;
3. **migration** — an explicit transformation that creates a new-version representation.

Reading an old record must never silently migrate or rewrite it.

## Motivation

Scientific releases are immutable evidence artifacts. A software upgrade must not make a
published Rejuv release unreadable, nor reinterpret it through a newer schema by default.

Without frozen historical readers, changing the current Pydantic model would also change
the meaning of old validation.

## Decisions

### D1. Released contracts live in immutable version packages

Version 0.1.0 lives under:

```text
rejuv.contracts.v0_1_0
```

A new schema version adds a new package. It does not edit the previous version to make
new data fit.

Bug fixes to a historical reader are allowed only when the implementation demonstrably
fails to enforce the already-published contract. Such changes require an RFC note and
compatibility tests.

### D2. Public top-level models are current-writer aliases

Imports such as:

```python
from rejuv.models import InterventionEpisode
```

mean "the current writer contract".

They are convenient for creating new data, but they are not the API for reading
arbitrary historical releases.

### D3. Historical data uses version-dispatch loaders

Use:

```python
load_intervention_episode(payload)
load_source_manifest(payload)
load_data_release_manifest(payload)
```

The loader reads the embedded contract version and dispatches to that frozen reader.

Unknown versions fail explicitly.

There is no "closest version", fallback parsing, or best-effort guessing.

### D4. Reading never migrates

A 0.1.0 payload loaded in future software remains a 0.1.0 model.

The reader must not insert fields from a newer version, rename historical fields,
rewrite version markers, or persist a migrated representation.

### D5. Migration is opt-in and non-mutating

Migration is a separate operation:

```python
migrate_payload(...)
migrate_intervention_episode(...)
```

Migration functions receive a copy and return a new payload.

Migration edges are explicit and composable. If no path exists, Rejuv raises
`MigrationNotAvailableError`; it does not invent one.

### D6. Migration does not replace the historical artifact

A migrated record is a derived representation. The original serialized record, release
manifest, checksum, and version remain authoritative evidence for the historical release.

### D7. Published read support is durable

Once a contract version appears in a published Rejuv data release, the main Rejuv reader
should retain support indefinitely where technically feasible.

A historical reader may be removed from the primary package only after an archived
validator, immutable public schema artifacts, a documented access/migration path, and an
explicit governance/RFC decision exist.

Pre-release experimental versions never used in a published release may be removed more freely.

### D8. Software and serialized contract versions are independent

Do not infer software version, episode schema version, source-manifest version, or
release-manifest version from one another.

## Adding 0.2.0

A future 0.2 implementation should:

1. leave `contracts/v0_1_0` intact;
2. add `contracts/v0_2_0`;
3. add 0.2 readers to the version registry;
4. point top-level writer aliases at 0.2;
5. update current-version constants;
6. add frozen 0.2 fixtures;
7. add explicit 0.1 -> 0.2 migration only if a defensible transformation exists;
8. verify that 0.1 fixtures still load through the 0.1 reader.

A schema bump does not imply that every old record can be losslessly migrated.

## Failure semantics

Unknown or malformed version markers are hard errors. Scientific infrastructure should
prefer an explicit unsupported contract over silently misinterpreted data.

## Non-goals

RFC-0003 does not define semantic parity between Pydantic and JSON Schema (#10),
canonical fingerprinting (#14), artifact/record topology (#11), or cross-version
benchmark comparability.

## Acceptance criteria

- 0.1 contracts are frozen in a versioned package;
- current writer imports preserve the existing public API;
- loaders dispatch using embedded versions;
- unsupported versions fail clearly;
- readers do not mutate input payloads;
- migration is explicit and non-mutating;
- frozen 0.1 episode/source/release fixtures continue to validate.
