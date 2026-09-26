# Roadmap

The roadmap optimizes for scientific usefulness and architectural stability, not feature count.

## Phase 0 — Foundation

**Goal:** establish contracts that are difficult to change later.

- [x] project charter and README;
- [x] architecture principles;
- [x] InterventionEpisode RFC;
- [x] initial schema implementation;
- [x] benchmark-spec format;
- [x] schema export consistency test;
- [ ] ontology mapping policy;
- [x] initial provenance/release manifest format;
- [x] initial source-adapter interface;
- [x] first CI validation workflow (runner availability currently external/blocking).

Exit criterion: public contracts have explicit structural and semantic validation rules,
and synthetic records are reproducibly traceable from source artifact to normalized
episode.

## Phase 0.5 — Foundation hardening gate

**Goal:** resolve migration-sensitive gaps found in the 2026-09-26 foundation audit
before real corpus ingestion.

P0 blockers:

- [x] #10 structural/semantic validation contract;
- [ ] #11 artifact vs logical-record provenance topology;
- [ ] #12 study/arm/contrast/statistical semantics;
- [x] #13 historical schema readers and migrations;
- [ ] #14 canonical fingerprint/reproducible build identity;
- [ ] #15 canonical intervention/experiment identity for leakage-safe splits.

Supporting work:

- [ ] #18 units/regimen/strain/ontology normalization;
- [x] #19 one local verification command independent of GitHub Actions.

See [foundation-audit-2026-09-26.md](foundation-audit-2026-09-26.md).

**Gate rule:** do not begin bulk real-data normalization while migration-sensitive P0
contracts are still unresolved. A tiny exploratory adapter/fixture is allowed only when
it is explicitly disposable and not treated as a release.

Exit criterion: a controlled lifespan experiment can be represented with truthful
provenance, control/contrast semantics, stable versioning, and reproducible identity.

## Phase 1 — Small high-quality corpus

**Goal:** prove heterogeneous intervention evidence can share one protocol.

Initial source families:

1. lifespan/healthspan interventions;
2. single-cell perturbation datasets;
3. rejuvenation/reprogramming datasets.

Targets:

- 500–2,000 carefully normalized InterventionEpisodes;
- explicit source licensing;
- reproducible adapters;
- curation levels;
- measured vs derived values preserved.

Exit criterion: an external contributor can reproduce a data release from manifests and permitted upstream sources.

## Phase 2 — RB01

**Goal:** publish the first useful benchmark.

RB01 evaluates unseen-intervention outcome prediction.

Required baselines:

- prevalence/majority;
- nearest-neighbor;
- linear/logistic;
- tree-based baseline.

Required outputs:

- direction;
- magnitude where meaningful;
- adverse-effect signal;
- uncertainty.

Exit criterion: benchmark split and metrics can be reproduced from a frozen data release.

## Phase 3 — Historical Replay

**Goal:** distinguish scientific prediction from retrieval/memorization as far as practical.

- define publication/data cutoffs;
- freeze pre-cutoff evidence;
- hold out post-cutoff experimental outcomes;
- document contamination limits;
- add replay manifests.

Exit criterion: at least one historical period can be replayed end-to-end.

## Phase 4 — Agent-native access

**Goal:** let AI systems use Rejuv without scraping docs.

- Python SDK stabilization;
- HTTP/OpenAPI service;
- MCP server;
- capability discovery;
- structured evidence-chain queries.

Exit criterion: an external agent can discover a benchmark, retrieve evidence, submit predictions, and receive evaluation through structured APIs.

## Phase 5 — RejuvGym

**Goal:** evaluate experiment selection, not only prediction.

- experiment-budget environments;
- historical ground-truth backend;
- information-gain/regret metrics;
- cost-aware experiment choice;
- uncertainty tracking.

Exit criterion: random, heuristic, Bayesian, and agent policies can be compared reproducibly.

## Phase 6 — Multiscale and temporal expansion

- cross-tissue benchmarks;
- cross-species transfer;
- longitudinal trajectories;
- intervention sequence effects;
- multimodal state representations;
- toxicity and oncogenic-risk endpoints where evidence permits.

## Phase 7 — Prospective collaboration

**Goal:** reduce dependence on historical ground truth.

Potential backends:

- unpublished partner datasets;
- organoid experiments;
- virtual-cell systems;
- robotic laboratory interfaces.

The agent-facing experiment contract should remain stable while the backend changes.

## Explicitly deferred

Until the core protocol is validated, do not prioritize:

- a consumer longevity app;
- elaborate dashboards;
- a proprietary foundation model;
- a new ontology;
- autonomous clinical recommendation;
- ingestion of all PubMed;
- infrastructure requiring distributed microservices.

A small reliable scientific substrate is more valuable than a large unreliable platform.
