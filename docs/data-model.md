# Data model

## Core abstraction

The primary entity is an **InterventionEpisode**.

It describes a biological system at baseline, an ordered intervention sequence, elapsed time, observed outcomes, and the evidence supporting those observations.

```text
BiologicalContext
      +
BaselineMeasurements
      +
Intervention[1..n]
      +
Time
      |
      v
Outcome[1..n] + AdverseEffect[0..n]
```

## Why this is the primary abstraction

Aging datasets are usually organized around papers, genes, compounds, or samples. Those are important entities but are poor interfaces for causal prediction.

An AI scientist needs examples that resemble:

```text
given state S
perform action A
wait T
observe state S'
```

InterventionEpisode makes this transition explicit.

## Entity overview

### Study

Represents the experimental study or dataset from which one or more episodes are derived.

A Study can contain multiple experimental arms and many InterventionEpisodes.

### BiologicalContext

Describes the system being acted upon.

Initial fields include:

- organism / NCBI Taxonomy reference;
- tissue / anatomy reference;
- cell type;
- sex when reported;
- chronological age when reported;
- disease or experimental state;
- genotype or relevant genetic background;
- donor or subject pseudonymous identifier when appropriate.

Missing information is represented as missing, never guessed.

### Intervention

An ordered action applied to the biological system.

Examples:

- compound exposure;
- gene knockout;
- gene suppression;
- gene activation;
- RNA intervention;
- genome editing;
- epigenome editing;
- partial reprogramming;
- dietary intervention;
- environmental intervention;
- cell therapy.

An intervention may contain:

- agent;
- biological target;
- dose;
- route;
- start offset;
- duration;
- protocol notes.

### Measurement

A measurement is an observation at a specific time or state.

Examples:

- gene expression;
- methylation age;
- protein concentration;
- grip strength;
- frailty index;
- tumor incidence;
- median lifespan.

Every value should state its origin when known:

- `measured`
- `author_reported`
- `derived`
- `inferred`
- `model_generated`

These categories must never be collapsed silently.

### Outcome

An outcome expresses the result relevant to the intervention question.

Initial outcome categories:

- molecular;
- cellular;
- functional;
- healthspan;
- lifespan;
- pathology;
- safety.

An outcome can include comparator, direction, magnitude, confidence/uncertainty, and evidence references.

### EvidenceReference

Connects a record to its evidence.

Possible identifiers include:

- DOI;
- PMID;
- preprint DOI;
- GEO;
- SRA;
- ArrayExpress/BioStudies;
- repository URL;
- figure/table/supplement locator.

### Provenance

Records how Rejuv obtained a value.

Examples:

- imported by adapter;
- extracted by parser;
- normalized by transformation;
- mapped to ontology;
- reviewed by a curator.

## Evidence maturity

Each record may have a curation level:

- **L0 Imported**: mechanically ingested, not reviewed;
- **L1 Normalized**: schema-valid and normalized;
- **L2 Human-reviewed**: evidence and interpretation checked by a reviewer;
- **L3 Benchmark-certified**: eligible for a specific benchmark release after quality checks.

A high curation level does not mean a biological claim is universally true. It describes the quality of the representation and evidence chain.

## Stable identifiers

Identifiers should be opaque and stable.

Suggested forms:

```text
rejuv:study:<uuid>
rejuv:episode:<uuid>
rejuv:intervention:<uuid>
rejuv:outcome:<uuid>
rejuv:evidence:<uuid>
```

Human-readable labels can change without breaking references.

## Time

Intervention science is temporal. Rejuv must represent:

- intervention start;
- intervention duration;
- measurement offset;
- follow-up duration;
- intervention order.

The v0.1 schema uses explicit numeric values with units rather than assuming a single timescale.

## Sequences

Multiple interventions are represented as an ordered list with independent timing.

Example:

```text
T+0d   senolytic
T+14d  immune intervention
T+30d  partial reprogramming
T+31d  stop expression
T+60d  measurement
```

This allows future benchmarks to compare `A -> B` with `B -> A`.

## Missingness

Do not encode missing values as:

- zero;
- empty strings;
- "unknown" free text where null is sufficient;
- inferred defaults.

If the reason for missingness matters, future schema versions may add explicit missingness semantics.

## Ontology strategy

Rejuv should prefer external identifiers.

Examples:

- organism: NCBITaxon;
- cell type: CL;
- anatomy: UBERON;
- chemical: CHEBI;
- disease: MONDO where appropriate;
- assay: OBI where appropriate.

Rejuv-local terms should be introduced only when no appropriate community concept exists.

## Safety semantics

Rejuv records published experimental protocols for scientific evaluation. Schema presence does not imply that an intervention is safe, effective, clinically appropriate, or suitable for humans.

No API should convert evidence records directly into human dosing or treatment recommendations.
