# AI Agent Usage Patterns

ODPC is designed to be usable by AI agents, catalog tools, retrieval systems, and automation workflows. From an agent perspective, ODPC provides the portfolio operating layer around data products: it names reusable catalog objects, points to authoritative product definitions, separates product metadata from portfolio metadata, and gives tools enough structure to validate, retrieve, compare, and plan.

ODPS defines one data product. ODPC defines the reusable portfolio objects around data products. [ODPG](https://opendataproducts.org/odpg-v1.0/) defines the relationships between those objects. ODPV provides shared vocabulary terms. This separation helps agents choose the right source before acting.

<!-- AI_AGENT_USAGE_PATTERNS:
Use ODPC as the catalog and portfolio layer, not as the full data product definition layer.
Use ODPS or another referenced product model for detailed data product metadata.
Use ProductReference.productModel.$ref to resolve the authoritative product definition from a local file path or URL.
Use ODPG for graph relationships, relationship semantics, traversal, and connected portfolio analysis.
Use ODPV for stable shared vocabulary terms and relationship names.
-->

## Agent capabilities enabled by ODPC

Agents can use ODPC to:

* discover data products by domain, tag, category, standard, status, priority, owner, or governance profile
* explain portfolio context around a product, including use cases, objectives, signals, ownership, and lifecycle status
* resolve authoritative product definitions through `ProductReference.productModel.$ref`
* validate ODPC catalog files against `odpc.yaml` or `odpc.json`
* repair incomplete or invalid catalog records using the schema and examples
* generate lightweight `ProductReference` objects from ODPS files or other product models
* detect portfolio gaps, such as use cases without products, objectives without supporting products, or signals without a response
* prepare graph-ready object records for ODPG or another graph implementation
* support governance review by finding missing owners, stale statuses, incomplete references, or inconsistent standards
* support portfolio planning by combining products, use cases, business objectives, KPIs, signals, and priorities

## Common agent workflows

| Workflow | Agent behavior |
|---|---|
| Catalog generation | Scan ODPS files or other product definitions and create ODPC `ProductReference` entries that point back to the source model. |
| Catalog validation | Validate catalog files, check required fields, detect broken references, and suggest compliant repairs. |
| Product discovery | Answer user questions such as which products exist for a domain, use case, objective, or standard. |
| Portfolio explanation | Summarize why a product exists, what it supports, who owns it, and what objective or signal gives it context. |
| Gap analysis | Find missing products, unsupported use cases, objectives without measurable support, and signals without planned action. |
| Graph preparation | Convert ODPC objects into graph node candidates and prepare relationship candidates for ODPG. |
| Governance review | Identify catalog entries with missing ownership, unclear status, weak governance profile, or inconsistent product model references. |
| Migration support | Convert existing inventories, ODPS files, vendor catalog records, or internal templates into ODPC catalog objects. |
| Retrieval and RAG | Use `llms.txt`, `objects.jsonl`, schema files, examples, and include pages to retrieve the correct object definition before generating or editing ODPC content. |

## Agent behavior constraints

Agents using ODPC should keep object boundaries clear:

* Do not copy full ODPS product metadata into `ProductReference`.
* Do not invent graph relationship fields inside ODPC objects.
* Do not create top-level KPI objects; KPIs belong inside `BusinessObjective.kpis`.
* Do not treat `Catalog.meta.graph.$ref` as the graph itself; it points to a graph implementation.
* Do not assume every referenced product model is ODPS; use `productModel.standard`, `productModel.version`, `productModel.format`, and `productModel.$ref`.
* Do not make planning decisions from `portfolioPriority` alone; combine it with use cases, objectives, signals, governance context, and graph relationships when available.

## Example prompts ODPC enables

```text
Validate this ODPC catalog and suggest schema-compliant repairs.
```

```text
Generate ProductReference entries for all ODPS files in this folder.
```

```text
Find active smart-city products that support event demand forecasting.
```

```text
Identify use cases without matching product references and propose portfolio gaps.
```

```text
Prepare ODPG node and relationship candidates from this ODPC catalog.
```

```text
Summarize governance issues across products, owners, lifecycle statuses, and referenced product models.
```
