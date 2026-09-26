# Contract versioning

## Which API should I use?

### Creating new data

Use the current writer API:

```python
from rejuv.models import InterventionEpisode
from rejuv.sources import SourceManifest
from rejuv.releases import DataReleaseManifest
```

These names intentionally move forward when Rejuv adopts a new current contract.

### Reading stored or external Rejuv data

Use version-dispatch loaders:

```python
from rejuv.versioning import (
    load_data_release_manifest,
    load_intervention_episode,
    load_source_manifest,
)
```

These inspect the serialized version marker and select a frozen historical reader.

## Why the distinction matters

Validating old stored data against the current writer is unsafe because future software
may use a newer contract. Use the version-dispatch loader instead.

## Frozen contracts

Released readers live under:

```text
src/rejuv/contracts/v0_1_0/
```

Do not edit a historical contract merely to support a new version. Add a sibling version
package instead.

## Migration

Reading and migration are intentionally separate.

```python
old = load_intervention_episode(payload)

# Only when explicitly desired:
new_payload = migrate_intervention_episode(payload, target_version="0.2.0")
```

If Rejuv has no registered migration path, migration fails. A new schema can contain
concepts that cannot be reconstructed from an older record; no automatic migration
should be invented in that case.

## Immutability

Migration never changes the input dictionary. When migrated data is persisted, it should
be treated as a derived artifact rather than a replacement for the historical source.

## Support policy

Published contract versions are expected to remain readable for the long term.
Software versions and serialized contract versions are independent.

See [RFC-0003](../rfcs/0003-contract-versioning.md).
