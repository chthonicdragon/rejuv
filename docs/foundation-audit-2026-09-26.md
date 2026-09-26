# Foundation audit — 2026-09-26

## Scope

This audit reviews the pre-alpha Rejuv foundation before real lifespan/healthspan,
single-cell perturbation, or rejuvenation datasets are ingested.

The goal is not to maximize issue count. It is to identify decisions that are cheap to
change now and expensive to migrate after published data releases or external users
exist.

## Executive conclusion

The core direction is strong:

- intervention-first modeling is a useful organizing principle;
- provenance and licensing are treated as first-class concerns;
- source-specific ingestion is isolated from the biological core;
- release lineage and content checksums were introduced early;
- benchmark leakage and uncertainty are already recognized as design concerns.

However, real-data ingestion should pause until the P0 items below are resolved.

The most important finding is that Rejuv currently has **four different contracts that
are not yet fully aligned**:

1. Python/Pydantic validation;
2. exported JSON Schema;
3. scientific semantics described in RFC/docs;
4. benchmark semantics implied by RB01.

If real data is normalized now, these differences will become migration debt.

---

## P0 findings — fix before the first real corpus

### F-01 — Python and JSON Schema do not enforce the same contract

**Issue:** #10

Several important invariants exist only in Pydantic model validators:

- non-synthetic evidence must contain a source pointer;
- intervention order must be unique and sorted;
- evidence references must resolve to declared evidence.

The generated JSON Schema does not encode all of those semantics. A non-Python
consumer can therefore accept records that Rejuv rejects.

**Risk:** two implementations of "valid Rejuv data".

**Direction:** explicitly separate structural validation from semantic validation,
publish both as versioned contracts, and add negative parity fixtures.

---

### F-02 — SourceArtifact and SourceRecord are conflated

**Issue:** #11

The current contract effectively models:

```text
one logical record -> one fetched artifact
```

Real scientific sources frequently look like:

```text
one TSV/H5AD/archive -> thousands or millions of logical records
```

The current model would either re-fetch/re-identify the same bytes for every record or
misrepresent provenance.

A normalized episode can also depend on several inputs, for example a paper,
supplement, and dataset. `DerivationRecord` currently has one input artifact.

**Risk:** false provenance and poor scaling on the first bulk dataset.

**Direction:** separate physical artifacts from logical source records and allow
many-to-many derivation.

---

### F-03 — The causal/experimental layer is missing

**Issue:** #12

Documentation describes a `Study`, but code currently stores only `study_id`.

The core cannot yet represent, in a machine-readable way:

- experimental arms/control groups;
- sample size;
- randomization/design;
- aggregate statistic type;
- censoring/survival semantics;
- structured confidence intervals;
- a formal contrast between treatment and control.

`Outcome` currently mixes raw observation and comparative effect semantics via
`effect_direction`, `value`, a free-text `comparator`, and one untyped
`uncertainty` float.

**Risk:** lifespan and perturbation evidence gets flattened into values that cannot later
support honest causal benchmarks.

**Direction:** distinguish observations/state from contrasts/effect estimates and add a
minimal Study/Arm/Design model before real ingestion.

---

### F-04 — Schema evolution is not yet historically readable

**Issue:** #13

Current classes are centered on the current version:

- `InterventionEpisode.schema_version` accepts only 0.1.0;
- release manifests require the current schema version;
- manifest contract versions are current-only literals.

That is fine for v0.1, but the first 0.2 change creates a conflict: immutable old
releases must remain readable without pretending they were authored under 0.2.

**Risk:** a future software upgrade makes old published releases invalid.

**Direction:** separate read-version dispatch, current writer models, migrations, and
frozen historical validators before schema 0.2.

---

### F-05 — Fingerprints are deterministic today, but not yet a long-term canonical contract

**Issue:** #14

`fingerprint_episode()` hashes sorted JSON produced from a Pydantic model dump.

Potential future drift sources include:

- Pydantic serialization changes;
- newly introduced default fields;
- numeric serialization;
- dependency-version differences.

The current determinism test compares two runs of the same implementation. Both can
change together and the test will still pass.

**Risk:** a published fingerprint becomes impossible to reproduce exactly later.

**Direction:**

- version the fingerprint/canonicalization profile;
- use a precisely specified canonical representation, preferably a standard such as
  RFC 8785 JCS or an equally explicit profile;
- add golden expected hashes;
- lock the data-build environment and/or record its digest.

---

### F-06 — RB01 intervention holdout is not leakage-safe yet

**Issue:** #15

`intervention_id` currently identifies an intervention instance in an episode.

It is not a canonical identity for "the same intervention" across studies.

Therefore:

```text
study A: rapamycin -> intervention_id A
study B: rapamycin -> intervention_id B
```

can enter train and test simultaneously while technically satisfying an
`intervention_id` holdout.

The same experiment can also arrive from several upstream sources.

**Risk:** benchmark scores look prospective while memorizing equivalent interventions
or duplicate experiments.

**Direction:** distinguish intervention instance, canonical intervention concept,
regimen/protocol signature, underlying experiment, and source record.

---

## P1 findings — design before the corresponding feature ships

### F-07 — Historical Replay lacks availability-time provenance

**Issue:** #16

`accessed_at` is not the date evidence became available.

Historical Replay needs explicit semantics for preprints, journal publication, dataset
versions, supplements, backfills, retractions, and superseded versions.

Do this before RB08, not after benchmark data exists.

---

### F-08 — Agent-native data creates an AI security boundary

**Issue:** #17

Upstream text is untrusted data.

Fields such as `protocol_text`, notes, titles, and source metadata can contain
instruction-like text. Future MCP agents must never treat it as trusted instructions.

Third-party adapters are executable Python and create a separate supply-chain boundary.

Human subject references also need explicit public/controlled/sensitive classification.

---

### F-09 — Units and biological normalization are too free-form for real corpus work

**Issue:** #18

Current weakly constrained fields include:

- `Quantity.unit`;
- dose regimen/frequency;
- route;
- strain/background;
- ontology namespace/id consistency.

This is acceptable for a synthetic contract but not a benchmark corpus.

A unit profile such as UCUM should be evaluated, while original source values should be
preserved alongside normalized values.

---

### F-10 — Local verification is not yet one reproducible operation

**Issue:** #19

GitHub Actions is currently unavailable on the maintainer account.

More importantly, project verification is spread across commands:

- schema check;
- pytest;
- Ruff;
- mypy (configured but not in the current workflow);
- examples/manifests.

Add one local verification entrypoint and make future CI call that same entrypoint.

---

## Additional semantic gaps found during review

These do not all need separate issues yet, but they should guide P0 RFC work.

### Baseline and outcome are asymmetric

The north-star model is:

```text
STATE(t0) + ACTION + TIME -> STATE(t1)
```

but `baseline` is a list of `Measurement`, while the post-intervention side is a
different `Outcome` abstraction.

For longitudinal/Virtual Cell work, a reusable `Observation` or `StateSnapshot`
model may be cleaner, with benchmark labels/effect estimates derived separately.

### Intervention order can disagree with time

The schema contains both `order` and `start`, but currently only checks that order
numbers are unique/sorted in serialization.

It is possible to encode:

```text
order 1 starts at day 30
order 2 starts at day 0
```

without stating what that contradiction means.

The model needs a single semantic definition of sequence/order.

### Repeated dosing is not machine-readable

Dose + duration + route cannot express many common protocols such as:

- daily;
- every other day;
- cycles;
- chow concentration;
- pulse treatment;
- induction/withdrawal schedules.

Do not hide the long-term machine-readable regimen entirely in `protocol_text`.

### Uncertainty is underspecified

A float called `uncertainty` does not state whether it is:

- standard deviation;
- standard error;
- confidence interval width;
- posterior uncertainty;
- measurement error;
- prediction probability.

This must be structured before quantitative benchmarks.

### Curation level is not strongly enforced

L2 means human-reviewed, but the model does not require a reviewer identity when L2/L3
is assigned.

That is a policy/validation gap.

### Provenance is not field-complete

`Provenance.source_record_id` does not include source namespace/id inside the episode
itself, and context fields do not have direct evidence links.

This becomes important when episodes combine several sources.

### Release reproducibility omits some declared requirements

The provenance docs mention build parameters and reproducibility, while the current
release manifest does not yet store:

- normalization configuration;
- random seed;
- external adapter code identity/checksum;
- build environment/lock digest;
- curation summary.

RFC-0002 says nondeterministic settings should be recorded, but the schema has no
dedicated field for them yet.

### Public contracts are not all exported language-neutrally

`InterventionEpisode` has a checked-in JSON Schema.

`SourceManifest` and `DataReleaseManifest` are public contracts but currently do not
have equivalent exported/check-drift schema artifacts.

### Package/runtime reproducibility is split

The development extra pins Pydantic, while the runtime dependency allows a wider
`pydantic>=2.9,<3` range.

That is reasonable for a library API, but not sufficient by itself for deterministic
scientific data builds. Data-build dependency identity should be explicit.

### Study/subject identity needs privacy semantics

`subject_id` is currently a free string.

For public releases it must mean a de-identified/pseudonymous dataset-local reference,
never a direct patient identifier. Controlled partner data will need stronger access
governance.

---

## Recommended repair order

Do not solve everything simultaneously.

### Gate A — make development safe

1. #19 — one local verification command;
2. #13 — historical version readers / evolution policy;
3. #10 — structural vs semantic validation contract.

### Gate B — make provenance truthful

4. #11 — artifact/record/derivation topology;
5. #14 — canonical fingerprint profile and golden hashes.

### Gate C — make biological meaning sufficient for real data

6. #12 — Study/Arm/Observation/Contrast/statistical semantics;
7. #18 — units, regimen, strain, ontology normalization.

### Gate D — make benchmarking honest

8. #15 — canonical intervention/experiment identity and leakage policy.

After Gates A-C, a small real-source pilot can begin safely.
Before publishing RB01, Gate D is mandatory.

Issues #16 and #17 should be completed before Historical Replay and agent-facing/MCP
surfaces respectively.

---

## What should not change

The audit does **not** recommend abandoning the central Rejuv idea.

Keep:

- `STATE + ACTION + TIME -> STATE` as the conceptual center;
- intervention-first data access;
- immutable source/release lineage;
- adapters isolated from core;
- external ontologies instead of a Rejuv ontology;
- simple baselines before foundation-model claims;
- historical replay and sequential discovery as long-term evaluation modes.

The changes above make those ideas enforceable rather than aspirational.

---

## External standards worth aligning with

- RFC 8785 JSON Canonicalization Scheme for stable hashable JSON:
  https://www.rfc-editor.org/rfc/rfc8785.html
- W3C PROV-DM for provenance concepts and derivation relationships:
  https://www.w3.org/TR/prov-dm/
- UCUM should be evaluated for normalized units:
  https://unitsofmeasure.org/

Rejuv does not need to adopt each standard wholesale. The goal is to avoid inventing
incompatible semantics where mature interchange standards already exist.

---

## Decision

**Pause Issue #3 real-data ingestion until the P0 foundation gate is resolved.**

Synthetic fixtures and RFC work can continue immediately.
