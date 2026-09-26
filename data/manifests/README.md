# Data manifests

This directory stores small, version-controlled manifests that describe how a Rejuv data
release is reconstructed.

Do not commit large upstream datasets here.

## Contract

The typed release contract lives in:

```text
src/rejuv/releases.py
```

A `DataReleaseManifest` identifies:

- Rejuv data-release id and version;
- Rejuv schema version;
- software version and code commit;
- exact upstream source manifests;
- fetched artifact metadata and SHA-256 checksums;
- adapter ids/versions;
- transformations;
- normalized episode fingerprints;
- ontology snapshots;
- curation/release notes.

## Identity rule

An upstream source version is descriptive provenance.

The authoritative identity of fetched content is:

```text
sha256(raw bytes)
```

If upstream content changes without its visible version changing, the Rejuv artifact
identity still changes.

## Reconstruction

Manifests should make a release auditable even when upstream data cannot legally be
redistributed.

A consumer should be able to determine:

```text
source snapshot
  -> artifact checksum
  -> adapter version
  -> transformations
  -> normalized episode checksum
```

See [docs/source-adapters.md](../../docs/source-adapters.md) and
[RFC-0002](../../rfcs/0002-source-adapter-release-manifests.md).
