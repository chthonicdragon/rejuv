# Source adapters and release manifests

## Purpose

Adapters let Rejuv ingest heterogeneous biological sources without coupling the core
protocol to any database, API, file format, or research domain.

The stable boundary is:

```text
upstream source
      |
   discover
      |
    fetch
      |
 raw artifact + SHA-256
      |
    parse
      |
 source-specific record
      |
  normalize
      |
InterventionEpisode
      |
  validate
```

## SourceAdapter

External adapters implement the `SourceAdapter` protocol in `rejuv.sources`.

The protocol deliberately does not prescribe HTTP libraries, databases, CLIs, or
storage systems.

### discover

Returns stable references to candidate source records.

Discovery should not change biological meaning or create inferred values.

### fetch

Retrieves the raw artifact and creates a `FetchedArtifact`.

The fetched payload verifies:

- SHA-256;
- byte length;
- source record identity;
- retrieval timestamp.

### parse

Converts raw bytes into source-specific structured records.

Parsing is still a representation of upstream data. It should not silently normalize
biology.

### normalize

Maps parsed source records into one or more `InterventionEpisode` objects.

Every inference or derivation introduced here must remain visible through provenance.

### validate

Runs source-specific invariants after core Pydantic validation.

Examples include:

- source-specific required identifiers;
- expected control-arm relationships;
- legal combinations of endpoint fields.

## Source manifests

`SourceManifest` records the exact upstream context used by an adapter.

It contains:

- source id/name/owner;
- homepage;
- source snapshot metadata;
- licensing and usage policy;
- update cadence;
- notes.

### Rights are explicit

Publicly downloadable does not mean freely redistributable or trainable.

Rejuv tracks separate states for:

```text
redistribution
derivative_data
commercial_use
model_training
```

Each is one of:

```text
allowed | prohibited | restricted | unknown
```

Use `unknown` rather than guessing.

## Version vs checksum

The source may report a version such as `2026.09`.

That is useful provenance, but **content identity is the SHA-256 checksum of the
artifact bytes**.

If a provider silently edits a file without changing its release version, Rejuv treats
the changed bytes as a different artifact.

## Release manifests

A `DataReleaseManifest` records the reproducible lineage of a Rejuv release.

```text
SourceManifest
      |
SourceArtifact -- SHA-256
      |
DerivationRecord -- adapter id/version + transforms
      |
NormalizedEpisodeRef -- episode id + SHA-256
      |
DataReleaseManifest
```

A release also records:

- Rejuv schema version;
- software version;
- code commit;
- ontology snapshots;
- release timestamp;
- episode count.

The manifest contains metadata, not raw third-party datasets.

## Deterministic normalization

`fingerprint_episode()` canonically serializes the normalized episode and hashes it.

The same raw input processed by the same deterministic adapter configuration should
produce the same episode fingerprint.

This provides a simple, testable invariant before Rejuv adds larger data pipelines.

## Future interoperability

This contract is intentionally compatible with future exports to:

- RO-Crate for research-object provenance;
- Croissant for machine-readable dataset metadata;
- object stores for large raw artifacts;
- external adapter packages;
- MCP tools for agent-driven ingestion and evidence inspection.

Those integrations should consume these contracts rather than replace them.
