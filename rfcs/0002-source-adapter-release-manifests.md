# RFC-0002: SourceAdapter and release manifest contracts

- **Status:** Accepted for initial implementation
- **Contract target:** 0.1.0
- **Scope:** source ingestion, licensing metadata, content identity, release lineage

## Summary

Define a stable boundary between RejuvCore and upstream biological data sources.

A source adapter must expose the conceptual pipeline:

```text
discover -> fetch -> parse -> normalize -> validate
```

Raw source identity is anchored by content checksums. A Rejuv data release records the
source snapshot, adapter version, raw artifact identity, transformations, normalized
episode fingerprints, ontology snapshots, software version, and code commit.

## Motivation

Upstream biological databases differ in APIs, identifiers, release cadence, licensing,
formats, and data quality. Rejuv must isolate those differences without leaking
source-specific fields into `InterventionEpisode`.

Reproducibility also requires more than an upstream version string. A source can change
content without changing a visible version. For that reason, content checksums are the
authoritative identity for fetched artifacts.

## Decisions

### D1. Source quirks remain behind adapters

Core biological models do not gain source-specific fields merely because one upstream
database needs them.

A core schema change requires an independent biological justification and RFC.

### D2. SHA-256 is the content identity for v0.1

Every fetched artifact used in a release must have a SHA-256 digest and byte length.

Additional checksum algorithms can be added later, but v0.1 intentionally has one
canonical algorithm.

### D3. Source version is descriptive, checksum is authoritative

`SourceSnapshot.version`, ETag, release date, and Last-Modified are useful provenance,
but they do not replace artifact checksums.

Two artifacts with the same source version and different SHA-256 values are different
inputs.

### D4. Rights metadata travels with the source

A source manifest records separate machine-readable statuses for:

- redistribution;
- derivative data;
- commercial use;
- model training;
- attribution requirement.

`unknown` is a valid and important state. Rejuv must not infer permission from public
accessibility.

### D5. Raw bytes do not belong in release manifests

`FetchedArtifact` can carry bytes during ingestion. Persistent manifests store only
artifact metadata and checksums.

Large or restricted upstream data can remain external.

### D6. Normalized episodes are fingerprinted canonically

A normalized episode is serialized as sorted UTF-8 JSON and hashed with SHA-256.

This allows a release to detect changes in normalization even when episode identifiers
remain unchanged.

### D7. Release manifests validate lineage

A release manifest rejects:

- duplicate source ids;
- duplicate artifact ids;
- artifacts referencing unknown sources;
- derivations referencing unknown artifacts;
- duplicate normalized episode ids;
- incorrect `episode_count`;
- schema-version mismatch.

### D8. Adapters are typed Python protocols, not framework plugins

The first implementation uses `typing.Protocol`.

This keeps external adapter packages possible without introducing a plugin framework,
entry-point registry, or service architecture before there is evidence they are needed.

## Contract sketch

```python
class SourceAdapter(Protocol):
    adapter_id: str
    adapter_version: str

    def source_manifest(self) -> SourceManifest: ...
    def discover(self) -> Iterable[SourceRecordRef]: ...
    def fetch(self, record: SourceRecordRef) -> FetchedArtifact: ...
    def parse(self, artifact: FetchedArtifact) -> Iterable[ParsedT]: ...
    def normalize(self, record: ParsedT) -> Iterable[InterventionEpisode]: ...
    def validate(self, episodes: Sequence[InterventionEpisode]) -> None: ...
```

## Determinism

Given the same:

- raw artifact bytes;
- adapter id/version;
- transformation configuration;
- schema version;
- ontology snapshots;

normalization should produce the same normalized episode fingerprints.

Sources that are intrinsically nondeterministic must record the relevant configuration
or seed in their transformation metadata.

## Non-goals

RFC-0002 does not define:

- network clients;
- authentication;
- a crawler;
- storage backends;
- controlled-access data governance;
- adapter discovery through package entry points;
- Croissant or RO-Crate export details.

Those can be layered on top of the core contract.

## Acceptance criteria

Issue #2 is complete when:

1. typed source and release models exist;
2. `SourceAdapter` is runtime-checkable;
3. license/usage metadata is explicit;
4. raw artifacts verify SHA-256 and byte length;
5. a synthetic adapter runs without network access;
6. repeated raw -> normalized runs produce identical episode fingerprints;
7. a release manifest validates lineage and rejects broken references;
8. documentation states source-version and checksum semantics.
