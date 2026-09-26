# Architecture

## Design objective

Rejuv is designed as a durable interface between biological evidence, predictive models, AI agents, and eventually experimental systems.

The project must remain useful if today's foundation models, model APIs, storage engines, or laboratory platforms are replaced. For that reason, the stable center of the architecture is the **intervention protocol**, not a particular model or database.

The canonical transition is:

```text
STATE(t0) + INTERVENTION SEQUENCE + TIME -> STATE(t1...n)
```

## Architectural principles

1. **Protocol before product.** Data contracts and evaluation semantics matter more than UI.
2. **Evidence is immutable.** Upstream facts are preserved; transformations create new layers.
3. **One-way derivation.** Raw -> normalized -> curated -> benchmark. Never overwrite a lower layer to match a higher one.
4. **Agent-native.** Important operations must be exposed through structured, machine-readable interfaces.
5. **Human-auditable.** Every benchmark result and derived value must be traceable.
6. **No ontology island.** Reuse established identifiers where possible.
7. **No model privilege.** Benchmarks must support simple statistical baselines, domain models, foundation models, and agents.
8. **Uncertainty is first-class.** Missingness, confidence, disagreement, and model uncertainty are represented explicitly.
9. **Safety by scope.** Rejuv is research infrastructure, not a system for autonomous clinical treatment.

## Layered architecture

```text
+---------------------------------------------------------------+
|                          Interfaces                           |
|             Python SDK | HTTP/OpenAPI | MCP                   |
+-------------------------------+-------------------------------+
                                |
+-------------------------------v-------------------------------+
|                         RejuvGym                              |
|       sequential experiment choice / budgeted discovery      |
+-------------------------------+-------------------------------+
                                |
+-------------------------------v-------------------------------+
|                         RejuvBench                            |
|  dataset splits | replay cutoffs | metrics | contamination    |
+-------------------------------+-------------------------------+
                                |
+-------------------------------v-------------------------------+
|                         RejuvGraph                            |
|      studies <-> episodes <-> evidence <-> ontology refs      |
+-------------------------------+-------------------------------+
                                |
+-------------------------------v-------------------------------+
|                         RejuvData                             |
|        normalized records | curated records | manifests      |
+-------------------------------+-------------------------------+
                                |
+-------------------------------v-------------------------------+
|                         RejuvCore                             |
| schema | validation | units | identifiers | provenance model  |
+---------------------------------------------------------------+
                                ^
                                |
+-------------------------------+-------------------------------+
|                         Adapters                              |
|  DrugAge | perturbation datasets | rejuvenation studies | ... |
+---------------------------------------------------------------+
```

## Storage strategy

Rejuv should not force every data type into one database.

### Metadata and event records

Use columnar tabular representations for releases:

- Apache Parquet
- Apache Arrow-compatible schemas
- DuckDB for local analytical access

### Large omics matrices

Use community-native formats rather than flattening them into relational tables:

- AnnData for annotated matrices
- Zarr where chunked/cloud-native access is appropriate

### Provenance

A release should be representable as a research object containing:

- source identifiers;
- checksums;
- adapter and parser versions;
- transformation steps;
- ontology snapshots;
- curation metadata;
- software commit;
- benchmark manifests.

RO-Crate-compatible export is a target.

### Dataset metadata

Dataset releases should expose machine-readable metadata. Croissant compatibility is a target.

## Source of truth

The Python domain models under `src/rejuv/` are the source of truth for the pre-1.0 schema implementation.

Checked-in JSON Schema files under `schemas/` are generated artifacts. Tests must fail if generated schema differs from the checked-in artifact.

At 1.0, schema governance may move to a language-neutral canonical specification if external consumers require it.

## Interfaces

### Python

Primary developer interface for local research workflows.

### HTTP/OpenAPI

Stable remote interface for datasets, evidence queries, benchmark execution, and result submission.

### MCP

Agent-facing interface. Planned tools include:

- `search_interventions`
- `get_episode`
- `get_evidence_chain`
- `list_benchmarks`
- `get_benchmark_spec`
- `submit_prediction`
- `evaluate_submission`
- `propose_experiment`

MCP tools must return structured data, stable identifiers, schema versions, and provenance references.

## Plugin boundaries

Adapters are replaceable plugins. The normative Python boundary is the
`SourceAdapter` protocol documented in [source-adapters.md](source-adapters.md) and
RFC-0002.

A source adapter implements:

```python
source_manifest()
discover()
fetch()
parse()
normalize()
validate()
```

Raw artifact identity is checksum-based. Source-reported version strings are provenance,
not sufficient content identity.

Benchmark tasks should also be pluggable:

```python
build()
split()
evaluate()
```

A new source or benchmark should not require changing core domain objects unless it reveals a genuine limitation in the protocol. Such changes require an RFC.

## Versioning

Serialized contracts use a split writer/reader model:

```text
current writer aliases
        |
        v
contracts/v0_1_0   contracts/v0_2_0   ...
        ^                 ^
        |                 |
        +---- version-dispatch reader
```

Historical records are validated with the frozen reader for the version embedded in the
record. Reading never migrates. Migration is an explicit derived-data operation.

See [versioning.md](versioning.md) and RFC-0003.

Three independent versions are required:

- **software version**: implementation package;
- **schema version**: data contract;
- **data release version**: immutable published evidence snapshot.

Example:

```text
software: 0.3.1
schema:   0.2.0
data:     2027.03
```

A benchmark run additionally records its benchmark-spec version.

## Future integration

The same high-level experiment interface should support multiple backends:

```text
HistoricalReplayBackend
VirtualCellBackend
PartnerDatasetBackend
RoboticLabBackend
```

An AI agent should not need to change its reasoning loop merely because ground truth moves from a historical dataset to a prospective experiment.

## External standards to interoperate with

Rejuv should map to, not replace:

- OBO Foundry ontologies;
- Cell Ontology (CL);
- UBERON anatomy;
- ChEBI chemicals;
- NCBI Taxonomy;
- OBI where appropriate;
- Croissant dataset metadata;
- RO-Crate provenance packaging;
- JSON Schema 2020-12;
- OpenAPI 3.x;
- AnnData / Zarr;
- Apache Arrow / Parquet.

Exact mappings belong in dedicated RFCs and schema modules.
