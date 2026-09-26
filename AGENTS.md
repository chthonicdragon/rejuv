# AGENTS.md

This file is the operating contract for AI coding and research agents working in Rejuv.

## Mission

Build reliable, auditable infrastructure for representing and evaluating biological interventions.

Optimize for:

1. scientific traceability;
2. stable machine-readable contracts;
3. reproducibility;
4. interoperability;
5. simple architecture.

Do not optimize for feature count or visual polish before these are secure.

## Non-negotiable scientific rules

Never:

- invent an experimental value, source, sample size, dose, identifier, or citation;
- infer a missing field unless the schema explicitly marks the value as inferred;
- convert an animal result into a human efficacy claim;
- treat biological-age change as equivalent to proven lifespan extension;
- discard null, neutral, failed, or harmful results because they are inconvenient;
- silently combine incompatible measurements;
- mark AI-extracted evidence as human-reviewed;
- turn Rejuv into clinical treatment or dosing advice.

If evidence is ambiguous, encode the ambiguity.

## Source hierarchy

When adding scientific evidence, prefer:

1. primary dataset / repository record;
2. primary paper;
3. supplementary material;
4. trusted curated database;
5. review article for context only.

Secondary summaries should not replace primary evidence when the primary source is accessible.

## Data-layer rule

Respect the derivation direction:

```text
raw -> normalized -> curated -> benchmark
```

Do not edit a lower layer to make a higher layer pass.

## Schema changes

Before modifying public model semantics:

1. inspect current RFCs;
2. determine whether the change can be represented using existing extension points;
3. if not, create/update an RFC;
4. document migration impact;
5. update Python models;
6. regenerate JSON Schema;
7. add compatibility tests;
8. update documentation.

Do not create project-local biological vocabulary when an established ontology identifier is suitable.

## Benchmark changes

Any benchmark change must consider:

- leakage;
- train/test similarity;
- time leakage;
- publication cutoff;
- duplicated biological experiments;
- donor/sample overlap;
- simple baselines;
- uncertainty calibration.

Never improve a leaderboard by weakening a split.

## Coding rules

- Python >= 3.12.
- Prefer typed, small modules.
- Pydantic models define pre-1.0 schema behavior.
- Avoid framework lock-in in core.
- No network access in unit tests.
- Deterministic transforms where possible.
- Pure functions for normalization where practical.
- Keep source adapters isolated from core.
- Add dependencies only when they remove meaningful complexity.

## Repository changes

Avoid:

- microservices before operational need;
- a heavy frontend before data contracts stabilize;
- premature distributed infrastructure;
- hidden magic in notebooks;
- giant generated files committed without justification.

Reusable logic belongs in packages, not only notebooks.

## Documentation requirement

When implementing a substantial concept, update the closest relevant file:

- architecture -> `docs/architecture.md`
- data semantics -> `docs/data-model.md`
- benchmark semantics -> `docs/benchmarking.md`
- evidence handling -> `docs/provenance.md`
- major design decision -> `rfcs/`

## Safety boundary

Rejuv may evaluate published research interventions and generate scientific hypotheses.

It must not autonomously prescribe, dose, or execute interventions on humans.

Any future physical-lab integration requires explicit safety, authorization, containment, and review layers outside the generic experiment-selection loop.

## Required verification

Before declaring a change complete, run:

```bash
python scripts/verify.py
```

This command is the authoritative local verification contract. GitHub Actions, when
available, must call the same command rather than duplicating project checks.

Do not claim verification passed if the command was not actually executed. If the
environment prevents execution, report that limitation explicitly.

## Definition of done

A change is done when:

- `python scripts/verify.py` passes, or an execution-environment limitation is explicitly documented;
- code works;
- tests cover the meaningful failure mode;
- provenance remains intact;
- schema/version implications are handled;
- docs reflect new semantics;
- no unsupported scientific claim was introduced.
