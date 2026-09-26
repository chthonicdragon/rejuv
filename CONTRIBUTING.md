# Contributing to Rejuv

Rejuv welcomes contributions from biology, geroscience, ML, data engineering, ontology, statistics, and agent-tooling communities.

## Contribution types

The preferred contribution boundaries are:

- **source adapter** — reproducibly ingest a public or appropriately licensed source;
- **ontology mapping** — improve identifier normalization;
- **curation** — review evidence and provenance;
- **benchmark** — add a scientifically justified evaluation task;
- **baseline** — add a reproducible comparison model;
- **core** — improve schema, validation, provenance, or interfaces.

## Before changing the schema

Do not casually add fields to `InterventionEpisode`.

Open an RFC when a change:

- modifies the meaning of an existing field;
- adds a cross-cutting biological concept;
- changes identifier semantics;
- changes benchmark comparability;
- breaks existing serialized records.

Small implementation fixes do not require an RFC.

For a new serialized contract version, do not modify an older frozen
`src/rejuv/contracts/vX_Y_Z/` package. Add a new version package, update the current
writer alias and version registry, and retain historical-reader tests. See
[docs/versioning.md](docs/versioning.md).

## Scientific integrity rules

Contributors and agents must:

1. never invent missing biological values;
2. preserve source meaning during normalization;
3. distinguish observation from derivation and inference;
4. preserve negative and neutral findings;
5. attach evidence identifiers/locators when available;
6. report uncertainty instead of hiding it;
7. avoid translating model-organism results into unsupported human claims;
8. keep research records separate from clinical advice.

## Development

Target runtime:

```text
Python >= 3.12
```

Recommended workflow:

```bash
uv sync --extra dev
uv run python scripts/verify.py
```

The project uses a `src/` layout.

### Authoritative verification

```bash
python scripts/verify.py
```

is the single project verification entrypoint. It runs schema drift checks, public
example/manifest validation, Ruff, mypy, and pytest. GitHub Actions is only another
runner for this command; correctness must not depend on GitHub-hosted runners.

## Tests

A change is not complete if it modifies:

- schema behavior without validation tests;
- benchmark splitting without leakage tests;
- normalization without representative fixtures;
- provenance without auditability tests.

## Data submissions

Do not commit large upstream datasets by default.

Prefer:

- persistent source IDs;
- checksums;
- manifests;
- adapter code;
- small legally redistributable fixtures.

Every adapter must document upstream licensing.

## AI-assisted contributions

AI assistance is welcome.

The contributor remains responsible for verifying:

- factual biological claims;
- citations and source locators;
- licensing;
- generated mappings;
- code behavior.

AI-generated extraction must not be labeled human-reviewed.

See [AGENTS.md](AGENTS.md).

## Pull requests

A good pull request explains:

- the problem;
- why the proposed abstraction is needed;
- compatibility impact;
- validation performed;
- scientific assumptions;
- unresolved uncertainty.

Prefer small, reviewable changes over broad rewrites.

## Commit style

Conventional-style prefixes are encouraged:

```text
feat:
fix:
docs:
schema:
data:
bench:
test:
refactor:
```

## Code of conduct

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
