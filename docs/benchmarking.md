# Benchmarking

## Objective

RejuvBench evaluates whether a model can generalize over biological interventions rather than merely retrieve familiar literature or interpolate within a narrow dataset.

A benchmark definition must state:

- eligible data release;
- inclusion/exclusion criteria;
- train/validation/test split logic;
- knowledge cutoff if applicable;
- target variables;
- metrics;
- contamination policy;
- uncertainty requirements;
- safety/toxicity targets;
- random seeds where relevant.

## Benchmark family

### RB01 — Unseen Intervention Outcome Prediction

**Question:** can a model predict the result of an intervention withheld from benchmark training?

Input:

```text
biological context
+ baseline state
+ intervention
```

Targets:

- effect direction;
- effect magnitude where comparable;
- toxicity/adverse outcome signal;
- calibrated uncertainty.

### RB02 — Unseen Intervention

A stricter holdout where test interventions are absent from train records.

### RB03 — Cross-Tissue Transfer

Train and test tissues are separated.

Example:

```text
train: blood, skin, liver
test:  muscle
```

### RB04 — Cross-Species Transfer

Tests whether effects learned in model organisms transfer to another species.

Example:

```text
train: mouse, fly, worm
test:  human cellular evidence
```

The benchmark must never treat model-organism lifespan gains as equivalent to demonstrated human lifespan extension.

### RB05 — Time Dynamics

Predicts a trajectory after an intervention rather than a single endpoint.

### RB06 — Rejuvenation vs Damage

A model must jointly reason about desired changes and safety.

Potential targets include:

- rejuvenation-associated molecular changes;
- preservation of cell identity;
- functional outcomes;
- toxicity;
- proliferative/oncogenic warning signals when available.

### RB07 — Sequence Effects

Compares order and timing of multiple interventions.

### RB08 — Historical Replay

Uses a strict publication/data cutoff.

Example:

```text
knowledge available through 2022-12-31
             |
             v
predict outcomes reported in 2023-2024
```

Historical replay is designed to test prospective-like scientific prediction with existing ground truth.

## Contamination policy

Historical replay is invalid if a model has access to the held-out result through:

- benchmark files;
- retrieval;
- prompt context;
- hidden metadata;
- later versions of a dataset.

Pretraining contamination cannot always be proven. Therefore benchmark reports must distinguish:

1. **data-pipeline isolation** — controlled by Rejuv;
2. **retrieval isolation** — controlled during evaluation;
3. **pretraining uncertainty** — often unknowable;
4. **closed-model limitations** — explicitly disclosed.

Future prospective partner datasets are preferred for high-confidence evaluation.

## Metrics

No single "Rejuvenation Score" should represent model quality.

Evaluation should expose a profile such as:

```text
effect_direction
effect_magnitude
toxicity_prediction
uncertainty_calibration
cross_tissue_transfer
cross_species_transfer
temporal_prediction
sequence_prediction
active_discovery_efficiency
```

Possible statistical metrics include:

- AUROC/AUPRC for categorical targets;
- MAE/RMSE for comparable continuous targets;
- Spearman/Pearson rank correlation where justified;
- Brier score / log loss for calibrated probabilities;
- expected calibration error;
- coverage of prediction intervals;
- regret and information gain for sequential discovery.

Metric selection is benchmark-specific and must be justified.

## Baselines

Every benchmark should include intentionally simple baselines.

Examples:

- majority / prevalence baseline;
- nearest-neighbor retrieval;
- linear/logistic model;
- tree-based model;
- simple tissue/species priors.

A complex model that fails to outperform a strong simple baseline has not demonstrated useful added capability.

## Benchmark-as-code

Benchmark specs live in `benchmarks/` and should be declarative where practical.

Example:

```yaml
name: rb01_unseen_intervention
version: 0.1.0
data_release: dev
split:
  strategy: intervention_holdout
targets:
  - effect_direction
  - adverse_effect
uncertainty:
  required: true
```

## Run manifests

Every submitted run should eventually emit:

```text
model
model_version
benchmark_version
data_release
schema_version
code_commit
environment
seed
predictions
metrics
timestamp
```

Results without enough metadata to reproduce or audit them should not be promoted as certified benchmark results.

## RejuvGym

RejuvGym extends static evaluation into sequential experiment selection.

An agent receives:

- current evidence;
- a set or generator of candidate experiments;
- an experiment budget;
- costs/constraints;
- hidden ground truth.

At each step it chooses an experiment and receives the stored outcome.

Core questions:

- How quickly does the agent reduce uncertainty?
- How many useful findings does it make per experiment?
- Does it avoid harmful or redundant choices?
- Is its uncertainty calibrated?
- Does it explore when needed and exploit when appropriate?

Historical data is the first backend. Future backends may include Virtual Cell systems and partner laboratories.
