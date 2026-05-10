# AI Agent Usage Guide

ODPC is designed to be usable by AI agents that generate, review, enrich, validate, or connect data product catalog information. Agents should treat ODPC as the catalog and portfolio layer of the OpenDataProducts.org standards family.

## Agent resource order

Agents SHOULD use ODPC resources in this order:

1. Fetch `/llms.txt` to understand the available resources and standards-family boundaries.
2. Use `/objects/odpc-objects.jsonl` for lightweight object selection, retrieval, and classification.
3. Use `/examples/*.yaml` when generating new ODPC catalog content.
4. Use `/schema/odpc.yaml` or `/schema/odpc.json` to validate catalog files.
5. Use the human-readable specification when object definitions, examples, and attribute explanations are needed.

When working from the source repository, agents MAY use the helper scripts in `scripts/`:

```bash
python3 scripts/check_agent_artifacts.py
python3 scripts/search_objects.py demand --json
python3 scripts/search_objects.py --id ProductReference
python3 scripts/validate_catalog.py source/examples/minimal-catalog.yaml
```

The validation script requires the packages listed in `scripts/requirements-agent.txt`.

## Common agent tasks

| Task | Recommended ODPC resource | Notes |
|---|---|---|
| Generate a new catalog | `/examples/minimal-catalog.yaml`, `/examples/full-catalog.yaml`, `/schema/odpc.yaml` | Start with the minimal catalog, then add reusable objects only when needed. |
| Convert product metadata into catalog form | `/examples/product-reference.yaml` | Use `ProductReference` and point `productModel.uri` to the authoritative product definition. |
| Classify demand or business need text | `/objects/odpc-objects.jsonl`, `/examples/use-case.yaml` | Use `UseCase` for demand-side needs and expected outcomes. |
| Classify strategic or operational outcomes | `/objects/odpc-objects.jsonl`, `/examples/business-objective-with-kpis.yaml` | Use `BusinessObjective`; nest KPIs inside `businessObjective.kpis`. |
| Capture evidence, risk, demand, or opportunity | `/examples/signal.yaml` | Use `Signal`; do not model relationships directly in the signal. |
| Build graph relationships between objects | ODPG resources | ODPC defines reusable objects. ODPG defines relationships, nodes, and edges. |
| Select stable terms or relationship names | ODPV resources | ODPV provides controlled vocabulary terms and relationship names. |

## Object choice rules

Agents SHOULD select the most specific ODPC object that matches the user's intent.

| User intent | Use | Avoid |
|---|---|---|
| "Create a catalog for these products and use cases" | `Catalog` | A full ODPS product document |
| "Add this product to a portfolio" | `ProductReference` | Copying all product metadata into ODPC |
| "Describe why the business needs data" | `UseCase` | `BusinessObjective` unless a strategic outcome is being defined |
| "Define the outcome we want to improve" | `BusinessObjective` | `UseCase` unless describing a concrete demand scenario |
| "Measure the objective" | `BusinessObjective.kpis` | A top-level `KPI` object |
| "Record evidence of demand, risk, or opportunity" | `Signal` | `KPI` or `BusinessObjective` |
| "Connect product A to use case B" | ODPG relationship | ODPC object fields |

## Generation rules

When generating ODPC YAML, agents SHOULD:

* include `schema`, `version`, and `catalog` at the document root
* use `version: "1.0"`
* use stable identifiers such as `CAT-001`, `DP-001`, `UC-001`, `BO-001`, `KPI-001`, and `SIG-001`
* use language-tagged strings such as `name.en` and `description.en`
* keep `ProductReference` lightweight and point to the authoritative product model with `productModel`
* nest KPIs inside `BusinessObjective`
* use `Signal` for observed evidence and recommended action
* use `x-` prefixed fields for local extensions
* validate the result with the ODPC schema

Agents SHOULD NOT:

* redefine ODPC object meanings
* use ODPC to describe full data product metadata that belongs in ODPS
* put graph edges, relationship semantics, or traversal rules inside ODPC objects
* invent top-level objects when an extension field or another standard is the correct place

## Validation and repair workflow

When repairing ODPC YAML, agents SHOULD:

1. Validate the file against `/schema/odpc.yaml` or `/schema/odpc.json`.
2. Check that required fields are present for `Catalog`, `ProductReference`, `UseCase`, `BusinessObjective`, and `Signal`.
3. Check that all human-readable names and descriptions use language-tagged strings.
4. Move full product metadata from `ProductReference` into the referenced product model when possible.
5. Move relationships into an ODPG graph file when possible.
6. Keep local additions under `x-` extension fields.
