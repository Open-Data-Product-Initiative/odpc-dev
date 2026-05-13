# Terms used

ODPC uses the [Open Data Product Vocabulary, ODPV](https://opendataproducts.org/odpv-v1.0/), as the shared vocabulary for the OpenDataProducts.org standards family. Use ODPV for common terms, stable ids, labels, definitions, aliases, and relationship names across ODPS, ODPC, and [ODPG](https://opendataproducts.org/odpg-v1.0/). For machine-readable lookup, use the ODPV term records at [ODPV terms.jsonl](https://opendataproducts.org/odpv-v1.0/vocab/terms.jsonl).

The terms below explain ODPC-specific usage where this specification gives a shared vocabulary term a concrete catalog-object shape, field-level meaning, or modeling constraint.

## Shared terms from ODPV

| Term | ODPV term | ODPC usage |
|---|---|---|
| Data product catalog | `DataProductCatalog` | Implemented in ODPC as the `Catalog` object. |
| Use case | `UseCase` | Implemented in ODPC as the `UseCase` object. |
| Business objective | `BusinessObjective` | Implemented in ODPC as the `BusinessObjective` object. |
| KPI | `KPI` | In ODPC, KPIs are nested inside `BusinessObjective.kpis`, not defined as top-level catalog objects. |
| Signal | `Signal` | Implemented in ODPC as the `Signal` object. |
| Data need | `DataNeed` | Represented in ODPC through `UseCase.dataNeeds`. |
| Data product graph | `DataProductGraph` | Referenced from ODPC through `Catalog.meta.graph`; graph structures belong to [ODPG](https://opendataproducts.org/odpg-v1.0/) or another graph standard. |
| Identifier | `Identifier` | Used in ODPC object `id` fields. |
| Reference | `Reference` | Used in ODPC for pointers such as `ProductReference.productModel.$ref` and `Catalog.meta.graph.$ref`. |
| Owner | `Owner` | Used in ODPC `owner` fields for accountable organizations, teams, or roles. |
| Domain | `Domain` | Used in ODPC `domains` and `scope.domains` fields for catalog grouping and filtering. |

## ODPC-specific usage notes

| Term | Description |
|---|---|
| `Catalog` | The ODPC object that implements an ODPV `DataProductCatalog`. It is the top-level portfolio container for product references, use cases, business objectives, signals, and catalog metadata such as ownership, scope, lifecycle status, tags, and graph implementation reference. |
| `ProductReference` | An ODPC-specific lightweight catalog object that identifies a data product and points to its authoritative product definition through `productModel`. It should not duplicate full ODPS product metadata. |
| `ProductModel` | The authoritative model or specification used to define a referenced data product, such as `ODPS`, `DPDS`, or an internal product model. In ODPC, `productModel.$ref` points to the source product definition as a local file path or URL. |
| `Portfolio object` | A reusable ODPC object used to manage a data product portfolio. Examples include `ProductReference`, `UseCase`, `BusinessObjective`, and `Signal`. |
| `Graph standard` | The graph standard used to implement catalog relationships through `Catalog.meta.graph`, such as [ODPG](https://opendataproducts.org/odpg-v1.0/), `RDF`, `JSON-LD`, `GraphML`, `openCypher`, `GQL`, `Gremlin`, `GraphSON`, or `GeoSPARQL`. |
| `Extension property` | A local or implementation-specific field whose name begins with `x-`. Extensions can add platform metadata without redefining official ODPC semantics. |

Relationship names such as `supports`, `requires`, `contributesTo`, `measures`, `dependsOn`, `providedBy`, and `consumedBy` should come from ODPV relationship terms and should be modeled in [ODPG](https://opendataproducts.org/odpg-v1.0/) or another graph standard, not as direct ODPC object fields.
