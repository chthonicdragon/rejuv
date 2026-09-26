# Data manifests

This directory stores small, version-controlled manifests that describe how a Rejuv data release is reconstructed.

Do not commit large upstream datasets here.

A future release manifest should identify:

- Rejuv data-release version;
- schema version;
- upstream source version/access date;
- persistent source identifiers;
- checksums where available;
- adapter version;
- transformation pipeline;
- ontology snapshots;
- licensing/usage metadata;
- curation state;
- code commit.

Manifests should make a release auditable even when upstream data cannot legally be redistributed.
