# Source adapters

Source adapters isolate upstream-specific parsing from RejuvCore.

A production adapter is expected to implement the conceptual stages:

```text
discover -> fetch -> parse -> normalize -> validate
```

Adapters must not silently invent missing values.

Each adapter should document:

- source identity;
- source version/update model;
- licensing;
- local caching rules;
- mapping to Rejuv entities;
- unsupported source fields;
- known ambiguities;
- representative tests/fixtures.

Source-specific quirks belong here, not in the core InterventionEpisode model.
