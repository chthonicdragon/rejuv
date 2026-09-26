# Data policy

## Purpose

Rejuv is intended to make biological intervention evidence machine-readable without erasing provenance, uncertainty, or upstream rights.

## No blanket relicensing

The Apache-2.0 license applies to Rejuv code, not automatically to third-party datasets.

Each source remains subject to its own license and terms.

## Default storage policy

Do not commit large third-party datasets to the repository by default.

Prefer:

- persistent accession/URL;
- content checksum;
- source version/date;
- adapter code;
- transformation manifest;
- small redistributable test fixtures.

## Required adapter metadata

A production source adapter must document:

- source owner;
- source URL/accession system;
- source license;
- redistribution permission;
- derivative-data constraints;
- model-training restrictions when stated;
- citation requirements;
- access date/version;
- expected update cadence.

## Sensitive data

The public Rejuv repository must not contain identifiable human subject data.

Future controlled-access datasets require separate authorization, access control, audit logging, and data-use governance. They must not be mixed into public releases.

## AI usage

Model-generated annotations are allowed only when:

- labeled as model-generated or AI-assisted;
- linked to their source material;
- reproducible enough to audit;
- not promoted to human-reviewed status automatically.

## Takedown and correction

If redistributed content is found to violate source terms or contain sensitive material, maintainers should remove it from active releases promptly and preserve only the minimum audit record needed to document the correction.
