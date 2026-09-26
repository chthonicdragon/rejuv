# Governance

## Current stage

Rejuv is currently founder-maintained and pre-1.0.

Governance is intentionally lightweight while the core protocol is being validated.

## Decision classes

### Routine implementation decisions

Maintainers may merge changes that do not alter public semantics.

Examples:

- bug fixes;
- tests;
- documentation;
- adapter implementation;
- performance improvements.

### Protocol decisions

Changes to schema semantics, benchmark meaning, evidence levels, or stable identifiers require an RFC.

RFC lifecycle:

```text
Draft -> Discussion -> Accepted/Rejected -> Implemented
```

Accepted RFCs become part of the project's architectural record.

### Scientific disputes

Rejuv should encode disagreement in data where possible rather than forcing governance to choose a biological "truth".

Examples:

- conflicting study outcomes;
- alternate ontology mappings;
- disputed rejuvenation biomarkers.

The goal is traceability and explicit assumptions.

## Maintainer responsibilities

Maintainers are responsible for:

- protecting schema compatibility;
- enforcing provenance requirements;
- preventing benchmark leakage;
- reviewing licensing constraints;
- separating scientific evidence from medical advice;
- documenting breaking changes.

## Future governance

If independent contributors or research groups begin depending on Rejuv, governance should evolve toward:

- multiple maintainers;
- domain reviewers for biology/ontology/benchmarking;
- public RFC discussions;
- published release criteria;
- conflict-of-interest disclosures for benchmark partners.

The project should not create a foundation, token, or elaborate governance structure before there is demonstrated community need.

## Neutrality

Rejuv should not privilege a company, model provider, intervention vendor, or longevity ideology.

Benchmark rules must apply equally to open and closed models where evaluation conditions permit.
