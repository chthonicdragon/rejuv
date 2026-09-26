# Provenance and evidence policy

## Principle

A scientific value without a traceable origin is not benchmark-grade evidence.

Rejuv therefore treats provenance as part of the data model, not as optional documentation.

## Data layers

```text
RAW
 |
 v
NORMALIZED
 |
 v
CURATED
 |
 v
BENCHMARK
```

### Raw

A reference or local cache of the upstream source as legally permitted.

Raw evidence is never edited to "fix" a downstream problem.

### Normalized

Source fields converted into Rejuv-compatible structure:

- units normalized where safe;
- identifiers mapped;
- obvious formatting harmonized;
- source meaning preserved.

### Curated

Human-reviewed interpretations and mappings.

Corrections create new provenance entries; they do not erase how a previous value was produced.

### Benchmark

A frozen selection with reproducible inclusion rules and split assignments.

## Value origin

Every value that could be confused with a direct observation should be classifiable as:

- `measured`
- `author_reported`
- `derived`
- `inferred`
- `model_generated`

Example:

```text
median_lifespan_days = 832
origin = author_reported
source = Figure 3 / Table S4
```

versus:

```text
lifespan_change_percent = 8.7
origin = derived
derived_from = [...]
transformation = percent_change_v1
```

These must remain distinguishable.

## Evidence references

Evidence references should be as specific as feasible.

Good:

```text
DOI + figure/table/supplement locator
GEO accession + sample IDs
repository release + file checksum
```

Weak:

```text
paper title only
"reported in literature"
LLM-generated summary without source locator
```

## AI extraction

AI may assist extraction, normalization, ontology mapping, and contradiction detection.

AI-generated content must never silently become L2 human-reviewed evidence.

Suggested provenance:

```text
extraction_method: ai_assisted
model: ...
prompt/template version: ...
source locator: ...
review_status: pending
```

## Conflicting evidence

Do not overwrite conflicting results with a consensus field.

Store the individual episodes and allow downstream analysis to model:

- organism differences;
- tissue differences;
- dose effects;
- protocol differences;
- study quality;
- uncertainty.

## Corrections

A correction should retain:

- previous record identifier/version;
- reason;
- author/agent;
- timestamp;
- source evidence;
- replacement value or mapping.

## Release provenance

A data release should record:

- source snapshots/checksums;
- adapter versions;
- schema version;
- ontology versions/snapshots;
- curation state;
- code commit;
- build parameters;
- license metadata.

RO-Crate-compatible packaging is a planned export target.

## Licensing

Rejuv does not assume that because data is publicly reachable it can be redistributed without restriction.

Each source adapter must document:

- upstream license;
- redistribution permissions;
- derivative-data constraints;
- commercial-use constraints where applicable;
- model-training restrictions where specified.

When redistribution is not allowed, Rejuv should prefer persistent identifiers, checksums, and reproducible transform recipes over copying the data.

## Audit question

For any benchmark value, the system should eventually be able to answer:

> Why does Rejuv contain this value, where did it come from, and what transformations produced it?

If that cannot be answered, the value is not ready for benchmark certification.
