# Security and responsible use

## Scope

Rejuv is research infrastructure for biological intervention data and model evaluation.

It is not designed to operate clinical systems or autonomously execute biological procedures.

## Reporting software vulnerabilities

Please open a private GitHub security advisory when available rather than a public issue for vulnerabilities that could expose credentials, private data, or controlled partner datasets.

## Scientific safety boundary

Rejuv may represent published interventions for benchmarking, but project interfaces should not directly convert records into:

- human treatment recommendations;
- personalized dosing instructions;
- autonomous clinical actions;
- unsupervised physical experiment execution.

Future laboratory integrations must add authorization, experimental safety review, containment rules, and hardware-specific controls outside the generic agent loop.

## Data security

Do not commit:

- credentials;
- private API keys;
- identifiable human subject data;
- controlled-access datasets;
- unpublished partner data without explicit authorization.

## Dependencies

Keep the core dependency surface small. Security updates to direct dependencies should be prioritized when they affect parsing, network-facing APIs, or data validation.
