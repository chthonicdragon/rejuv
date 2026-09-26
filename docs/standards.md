# Interoperability standards

Rejuv should contribute a missing intervention/evaluation layer rather than invent replacements for mature scientific standards.

## Current interoperability targets

| Concern | Preferred standard/ecosystem | Rejuv role |
|---|---|---|
| Organisms | NCBI Taxonomy | reference IDs |
| Cell types | Cell Ontology (CL) | reference IDs |
| Anatomy | UBERON | reference IDs |
| Chemicals | ChEBI | reference IDs |
| Disease concepts | MONDO where appropriate | reference IDs |
| Experimental concepts | OBI where appropriate | reference IDs |
| Tabular releases | Apache Parquet / Arrow | release format |
| Local analytics | DuckDB | consumer tool, not protocol |
| Single-cell matrices | AnnData | external/linked payload |
| Chunked arrays | Zarr | external/linked payload |
| Dataset metadata | Croissant | export/interoperability target |
| Research provenance | RO-Crate | release packaging target |
| Schema exchange | JSON Schema 2020-12 | generated contract |
| Remote APIs | OpenAPI 3.x | service contract |
| Agent interface | Model Context Protocol | structured agent tools |

## Principles

### Reuse identifiers

If a stable community identifier exists, store it rather than minting a Rejuv synonym.

### Preserve upstream semantics

Normalization should make data interoperable without flattening biologically meaningful distinctions.

### Extensions are namespaced

Future source-specific extensions should not pollute the core schema. Extension mechanisms should be specified through RFCs.

### Machine-readable rights

A future release manifest should expose source licensing and usage constraints in a machine-readable form where upstream terms permit.

## Links

- OBO Foundry: https://obofoundry.org/
- Cell Ontology: https://obofoundry.org/ontology/cl.html
- UBERON: https://obofoundry.org/ontology/uberon.html
- ChEBI: https://www.ebi.ac.uk/chebi/
- Croissant: https://mlcommons.org/working-groups/data/croissant/
- RO-Crate: https://www.researchobject.org/ro-crate/
- AnnData: https://anndata.readthedocs.io/
- Zarr: https://zarr.dev/
- Apache Arrow: https://arrow.apache.org/
- JSON Schema: https://json-schema.org/
- OpenAPI: https://www.openapis.org/
- Model Context Protocol: https://modelcontextprotocol.io/
