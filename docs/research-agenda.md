# Research agenda

## Central hypothesis

A major bottleneck in AI-driven biology is not the absence of observations, but the absence of a reliable, intervention-centered substrate for evaluating causal and temporal generalization.

Rejuv tests the hypothesis that biological AI should be evaluated on transitions:

```text
STATE + ACTION + TIME -> NEXT STATE
```

rather than primarily on reconstruction, embedding quality, or random held-out observations.

## Research questions

### RQ1 — Can models predict unseen interventions?

Can a model predict effect direction, magnitude, adverse outcomes, and uncertainty for interventions withheld from benchmark training?

### RQ2 — Does biological knowledge transfer across context?

How well do predictions transfer across:

- cell types;
- tissues;
- ages;
- genetic backgrounds;
- species?

### RQ3 — Can models predict trajectories rather than endpoints?

Can a model predict biologically meaningful intermediate states after an intervention?

### RQ4 — Can models distinguish apparent rejuvenation from damage?

A useful system must not optimize one biomarker while ignoring:

- loss of cell identity;
- toxicity;
- proliferative risk;
- functional decline.

### RQ5 — Does intervention order matter, and can AI learn it?

Can models learn that:

```text
A -> B
```

may differ from:

```text
B -> A
```

even when the same interventions are used?

### RQ6 — Can historical evidence support prospective-like evaluation?

Using knowledge cutoffs, can models predict experiments published later without access to post-cutoff evidence?

### RQ7 — Can an AI choose better experiments?

Given a fixed experimental budget, can an agent outperform:

- random selection;
- simple heuristics;
- uncertainty sampling;
- Bayesian optimization;

in discovery efficiency?

## Why aging first

Aging is an unusually useful stress test because useful models must integrate:

- molecular and functional outcomes;
- long time horizons;
- multiple tissues;
- multiple species;
- safety;
- combinations and sequences;
- weak correspondence between some biomarkers and organism-level outcomes.

The protocol itself should remain general enough to expand beyond aging.

## Falsifiable project-level claims

Rejuv should be willing to discover that its premise is wrong.

Examples of useful negative results:

- sophisticated models do not beat simple baselines;
- cross-species transfer is too weak for a proposed task;
- historical replay is dominated by pretraining contamination;
- a benchmark target is not reproducibly measurable;
- heterogeneous source data cannot support a fair comparison.

Publishing these failures is part of the research value.

## Long-term progression

```text
retrospective evidence
        |
        v
historical replay
        |
        v
sequential historical discovery
        |
        v
blind partner datasets
        |
        v
virtual-cell backends
        |
        v
prospective experimental collaboration
```

The agent-facing contract should remain as stable as possible while the source of ground truth becomes progressively more prospective.
