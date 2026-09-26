# Rejuv

**Open, agent-native infrastructure for representing, replaying, and benchmarking biological interventions across cells, tissues, organisms, and time.**

> **Status:** pre-alpha / research infrastructure. Rejuv is not a clinical decision-support system and must not be used to prescribe, recommend, or optimize treatments for people.

## Why Rejuv exists

AI biology is improving quickly, but evaluation is still fragmented. Datasets commonly describe observations, while the questions that matter for intervention science are causal and temporal:

```text
STATE(t0) + INTERVENTION + TIME  ->  STATE(t1)
```

Rejuv makes that transition the primary unit of data.

The first domain is aging and rejuvenation because it exposes several hard problems at once: cross-species transfer, tissue specificity, longitudinal effects, toxicity, multimodal measurements, sequencing of interventions, and the gap between molecular biomarkers and functional outcomes.

The long-term goal is broader: a reusable protocol and evaluation environment for AI-driven experimental biology.

## Core ideas

### 1. InterventionEpisode

The canonical record is an **InterventionEpisode**: a biological context, one or more interventions, elapsed time, resulting measurements, outcomes, adverse effects, and traceable evidence.

### 2. Evidence before scores

Every derived claim should be traceable to its source, extraction step, transformation, ontology mapping, and benchmark release.

### 3. Historical replay

Benchmarks can enforce a knowledge cutoff and ask a model to predict results published later. This is designed to reduce contamination and test whether a system can generalize beyond memorized literature.

### 4. Sequential discovery

RejuvGym will evaluate agents that choose the next experiment under a limited budget. The objective is not merely benchmark accuracy, but useful discovery per experiment.

### 5. Agent-native by design

Schemas are machine-readable, benchmark definitions are declarative, provenance is explicit, and the project is designed to expose Python, HTTP/OpenAPI, and MCP interfaces.

## Architecture

```text
                           REJUV
                             |
             +---------------+---------------+
             |                               |
         RejuvCore                       RejuvData
    schema + validation            normalized evidence
             |                               |
             +---------------+---------------+
                             |
                         RejuvGraph
                  evidence + interventions
                             |
                 +-----------+-----------+
                 |                       |
             RejuvBench              RejuvGym
           static evaluation     sequential discovery
                 |                       |
                 +-----------+-----------+
                             |
                          Rejuv API
                    Python / HTTP / MCP
                             |
                    models and AI agents
                             |
                 virtual or physical labs
```

See [docs/architecture.md](docs/architecture.md).

## Initial benchmark

The first target is **RB01: Unseen Intervention Outcome Prediction**.

Input:

```text
biological context + baseline state + intervention
```

Output:

```text
direction + magnitude + toxicity/adverse effects + uncertainty
```

The test split must contain interventions not available to the model through the benchmark training data. Later releases add tissue holdouts, cross-species transfer, time dynamics, sequence planning, and historical replay.

See [docs/benchmarking.md](docs/benchmarking.md).

## Repository layout

```text
rejuv/
├── src/rejuv/          # core Python package
├── schemas/            # normative JSON Schemas
├── adapters/           # source-specific ingestion adapters
├── benchmarks/         # declarative benchmark specifications
├── data/manifests/     # release manifests, never raw upstream data by default
├── docs/               # architecture and policies
├── rfcs/               # design proposals
├── tests/
├── AGENTS.md            # operating contract for AI coding/research agents
└── pyproject.toml
```

## Data principles

Rejuv follows several rules from the first release:

- raw upstream evidence is never silently rewritten;
- normalized, curated, and benchmark layers are distinct;
- measured, author-reported, derived, inferred, and model-generated values are distinguishable;
- ontology identifiers are preferred over project-local biological vocabularies;
- licenses and permitted uses stay attached to sources;
- benchmark splits are reproducible and versioned;
- uncertainty and missingness are first-class data, not empty strings;
- negative, neutral, and harmful outcomes are valuable evidence.

The project is designed to interoperate with established standards rather than replace them. Planned mappings include OBO ontologies, Croissant dataset metadata, RO-Crate provenance, Parquet/Arrow for tables, and AnnData/Zarr for large omics matrices.

## MVP

The first useful release is intentionally small:

1. stabilize `InterventionEpisode` v0.1;
2. ingest a limited, high-quality subset from three source families:
   - lifespan / healthspan intervention evidence,
   - single-cell perturbation datasets,
   - cellular rejuvenation / reprogramming datasets;
3. publish 500–2,000 reviewed episodes rather than millions of weak records;
4. ship RB01 with simple baselines;
5. add a reproducible historical-replay split;
6. expose a stable Python API before building a substantial UI.

See [docs/roadmap.md](docs/roadmap.md).

## Local verification

After installing development dependencies:

```bash
python -m pip install -e ".[dev]"
python scripts/verify.py
```

With uv:

```bash
uv sync --extra dev
uv run python scripts/verify.py
```

The same command is used by CI when GitHub Actions runners are available.

## Non-goals

Rejuv is **not**:

- a longevity recommendation app;
- a biological-age score for consumers;
- a replacement for wet-lab validation;
- a new biological ontology;
- a foundation model;
- a medical device;
- a claim that any intervention extends human lifespan.

## Contributing

The project is designed for contributions from biologists, ML researchers, data engineers, ontology maintainers, and AI agents. The main contribution types are:

- source adapters;
- ontology mappings;
- curated evidence;
- benchmark definitions;
- baseline models;
- evaluation and contamination tests.

Read [CONTRIBUTING.md](CONTRIBUTING.md), [GOVERNANCE.md](GOVERNANCE.md), and [AGENTS.md](AGENTS.md) before substantial changes.

## Design RFCs

Major schema or benchmark changes require an RFC. Current accepted foundation RFCs:

- [RFC-0001: InterventionEpisode v0.1](rfcs/0001-intervention-episode.md)
- [RFC-0002: SourceAdapter and release manifest contracts](rfcs/0002-source-adapter-release-manifests.md)

The current foundation audit and hardening gate are documented in
[docs/foundation-audit-2026-09-26.md](docs/foundation-audit-2026-09-26.md).

## Safety and scientific scope

Rejuv stores and evaluates published or appropriately licensed research evidence. It should support scientific hypothesis generation, not unsupervised clinical experimentation. Human-treatment recommendations, dosing advice, or autonomous execution of experiments involving people are outside the project scope.

## License

Code is licensed under the Apache License 2.0. Dataset releases retain source-compatible licensing and provenance; Rejuv does not claim rights over upstream data.

---

**North-star question:** *Can an AI system predict a biological intervention it has not seen, know when it is uncertain, and choose the next experiment that most efficiently reduces that uncertainty?*
