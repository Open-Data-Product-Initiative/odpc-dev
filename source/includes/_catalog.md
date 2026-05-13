# ODPC Catalog

The `Catalog` object defines a reusable ODPC catalog. It provides the top-level structure for organizing product references, use cases, business objectives, signals, and catalog metadata such as ownership, scope, lifecycle status, tags, and graph implementation.

<img src="/images/catalog.png" width="500">

In ODPC, the `Catalog` object acts as the portfolio container. It helps organizations group related data products and demand-side objects around a domain, organization, geography, audience, or strategic theme.

The `Catalog` object can include product references, use cases, business objectives, and signals directly as reusable catalog objects. It can also define where the catalog graph is implemented through the `meta.graph` attribute.

The `meta.graph` attribute identifies the graph standard, version, and reference used for the catalog graph. The graph can be implemented with [ODPG](https://opendataproducts.org/odpg-v1.0/) or another supported graph standard, such as `RDF`, `JSON-LD`, `GraphML`, `openCypher`, `GQL`, `Gremlin`, `GraphSON`, or `GeoSPARQL`.

The `Catalog` object should remain focused on catalog structure and portfolio organization. It should not define detailed product metadata, relationship semantics, nodes, edges, or graph rules. Detailed product definitions belong to product models such as `ODPS`. Relationship modeling belongs to the selected graph standard, with [ODPG](https://opendataproducts.org/odpg-v1.0/) as the native standard for the OpenDataProducts.org specification family.

By defining catalogs as reusable objects, ODPC supports discovery, portfolio browsing, governance review, prioritization, filtering, AI-assisted portfolio analysis, and reporting across data product ecosystems.

## Mandatory attributes and options

> Example of catalog object usage:

```yml
schema: https://opendataproducts.org/odpc-v1.0/schema/odpc.yaml
version: "1.0"
catalog:
  meta:
    id: CAT-001
    name:
      en: Urban Mobility Data Product Catalog
    description:
      en: Catalog of data products, use cases, objectives, 
          and signals related to urban mobility.
```


| Attribute | Type | Required | Description |
|---|---|---:|---|
| `schema` | string | ✓ | URI of the ODPC catalog schema used to validate the catalog file. |
| `version` | string | ✓ | Version of the ODPC specification used by the catalog file. |
| `catalog` | object | ✓ | Top-level object that defines an ODPC catalog. |
| `meta` | object | ✓ | Catalog metadata, including identity, purpose, ownership, scope, lifecycle, and graph reference. |
| `meta.id` | string | ✓ | Stable identifier for the catalog. |
| `meta.name` | object | ✓ | Human-readable catalog name using language-tagged strings. |
| `meta.name.en` | string | ✓ | English catalog name. |
| `meta.description` | object | ✓ | Short explanation of the catalog purpose and scope using language-tagged strings. |
| `meta.description.en` | string | ✓ | English catalog description. |


## Optional attributes and options

> Example of catalog object usage:

```yml
catalog:
  meta:
    id: CAT-001
    name:
      en: Urban Mobility Data Product Catalog
    description:
      en: Catalog of data products, use cases, objectives, 
          and signals related to urban mobility.

    owner:
      organization: Example Transport Authority
      team: Business Analytics
      role: Data Product Portfolio Manager

    scope:
      domains:
        - smart-city
        - mobility
        - transport
      geography: Abu Dhabi
      audience:
        - internal
        - public

    version: "1.0.0"
    status: active

    graph:
      standard: ODPG
      version: "1.0"
      $ref: https://example.org/graphs/urba.graph.yaml
    tags:
      - smart-city
      - mobility
      - events

  productReferences:
    - id: DP-001
      productID: urbanpulse-events
      productVersion: "1.0.0"
      name:
        en: UrbanPulse Events Data Product
      description:
        en: Data product providing event information for 
            urban analytics and citizen services.
      productModel:
        standard: ODPS
        version: "4.1"
        format: yaml
        $ref: ./products/urba/odps.yaml

  useCases:
    - id: UC-001
      name:
        en: Event Demand Forecasting
      description:
        en: Forecast event-related demand to improve 
            mobility planning and citizen services.

  businessObjectives:
    - id: BO-001
      name:
        en: Improve Urban Mobility Efficiency
      description:
        en: Reduce travel delays and improve movement 
            across the city through better data-driven 
            planning and operations.

  signals:
    - id: SIG-001
      name:
        en: Increasing Event Demand
      description:
        en: Indicates rising demand for event-related 
            mobility and public service planning.

```

| Attribute | Type | Required | Description |
|---|---|---:|---|
| `meta.owner` | object |  | Ownership information for the catalog. |
| `meta.owner.organization` | string |  | Organization responsible for the catalog. |
| `meta.owner.team` | string |  | Team responsible for the catalog. |
| `meta.owner.role` | string |  | Responsible role, such as `Data Product Portfolio Manager`. |
| `meta.scope` | object |  | Business, organizational, geographic, or audience scope of the catalog. |
| `meta.scope.domains` | array of strings |  | Domains covered by the catalog. |
| `meta.scope.geography` | string |  | Geographic scope of the catalog, if relevant. |
| `meta.scope.audience` | array of strings |  | Intended audience for catalog use, such as `internal`, `partner`, `public`, or `commercial`. |
| `meta.version` | string |  | Catalog version. |
| `meta.status` | string |  | Lifecycle status of the catalog, such as `draft`, `active`, `deprecated`, or `retired`. |
| `meta.graph` | object |  | Defines the graph specification used to describe relationships between catalog objects. |
| `meta.graph.standard` | string |  | Graph standard used for the catalog graph. Default is [ODPG](https://opendataproducts.org/odpg-v1.0/) for Open Data Product Graphs. Other options: `RDF` for semantic web graphs, `JSON-LD` for linked data in JSON, `GraphML` for graph exchange, `openCypher` for property graph scripts, `GQL` for ISO property graph queries, `Gremlin` for graph traversal, `GraphSON` for TinkerPop-style graph JSON, or `GeoSPARQL` for geospatial RDF graphs. |
| `meta.graph.version` | string | ✓ when `meta.graph` is used | Version of the graph standard. |
| `meta.graph.$ref` | string | ✓ when `meta.graph` is used | File path or URL pointing to the graph definition. |
| `meta.tags` | array of strings |  | Keywords used for search, grouping, filtering, and portfolio analysis. |
| `productReferences` | array of objects |  | List of data product references included in the catalog. Each item follows the `ProductReference` object schema. |
| `useCases` | array of objects |  | List of use cases included in the catalog. Each item follows the `UseCase` object schema. |
| `businessObjectives` | array of objects |  | List of business objectives included in the catalog. Each item follows the `BusinessObjective` object schema. |
| `signals` | array of objects |  | List of signals included in the catalog. Each item follows the `Signal` object schema. |
