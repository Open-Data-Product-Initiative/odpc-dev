# Catalog Toolkit

> Snippet of YAML version:

```yml
schema: https://opendataproducts.org/odpc-v1.0/schema/odpc.yaml
version: "1.0"
kind: Catalog
catalog:
  metadata:
    id: CAT-001
    name:
      en: Urban Mobility Data Product Catalog
    description:
      en: Catalog of data products, use cases, objectives, 
          and signals related to urban mobility.
    graph:
      standard: ODPG
      version: "1.0"
      $ref: https://example.org/graphs/urban-mobility.graph.yaml
```

ODPC is published in several forms for different users and tools. This specification provides the human-readable documentation, while the schema, catalog object records, and example files provide machine-readable resources for validation, catalog integration, AI retrieval, and automation. Use `odpc.yaml` or `odpc.json` to validate catalog files, `objects.jsonl` for lightweight object selection and retrieval, and the catalog examples when generating or repairing ODPC YAML.

The [ODP Agent SDK](https://github.com/Open-Data-Product-Initiative/odp-agent-sdk) is the primary implementation toolkit for the OpenDataProducts.org standards family. Use it when building agents or automation that need to work across ODPS, ODPC, ODPG, and ODPV instead of treating each standard as a separate one-off integration.

<!-- AI_AGENT_GUIDANCE:
Use /schema/odpc.yaml or /schema/odpc.json to validate ODPC catalog files.
Use /catalog/objects.jsonl for retrieval, classification, object selection, and lightweight tool calls.
Use /catalog/examples/*.yaml when generating or repairing ODPC catalog content.
Use the ODP Agent SDK as the main family-level toolkit when building agents that need ODPS, ODPC, ODPG, and ODPV support.
Use ProductReference for lightweight references to data products; do not copy full ODPS product metadata into ODPC.
Use BusinessObjective.kpis for KPIs; do not create top-level KPI objects.
Use [ODPG](https://opendataproducts.org/odpg-v1.0/), not ODPC, for graph relationships, nodes, edges, traversal, and relationship semantics.
Use ODPV when stable vocabulary terms or relationship names are needed.
-->

| Resource | Format | Purpose |
|---|---|---|
| [ODP Agent SDK](https://github.com/Open-Data-Product-Initiative/odp-agent-sdk) | SDK | Main toolkit for building agents and automation across ODPS, ODPC, ODPG, and ODPV |
| [`llms.txt`](/llms.txt) | Text | AI agent guidance for discovering and using ODPC resources |
| [`odpc.yaml`](/schema/odpc.yaml) | YAML Schema | YAML representation of the ODPC validation schema |
| [`odpc.json`](/schema/odpc.json) | JSON Schema | JSON representation of the ODPC validation schema |
| [`objects.jsonl`](/catalog/objects.jsonl) | JSONL | Agent-friendly one-object-per-line file for retrieval, classification, and lightweight tools |
| [`minimal.yaml`](/catalog/examples/minimal.yaml) | YAML | Minimal valid ODPC catalog example |
| [`full.yaml`](/catalog/examples/full.yaml) | YAML | Full catalog example with product references, use cases, business objectives, KPIs, and signals |
| [`product-reference.yaml`](/catalog/examples/product-reference.yaml) | YAML | Standalone ProductReference example |
| [`use-case.yaml`](/catalog/examples/use-case.yaml) | YAML | Standalone UseCase example |
| [`business-objective-with-kpis.yaml`](/catalog/examples/business-objective-with-kpis.yaml) | YAML | Standalone BusinessObjective example with nested KPIs |
| [`signal.yaml`](/catalog/examples/signal.yaml) | YAML | Standalone Signal example |

Agent-oriented helper scripts are available in the source repository for maintaining and using the catalog artifacts.

<!-- AI_AGENT_SCRIPT_GUIDANCE:
When working from the source repository, use scripts/search_objects.py for repeatable local ODPC object lookup.
Use scripts/search_objects.py --json when another tool or agent will consume the result.
Use scripts/validate_catalog.py to validate ODPC YAML or JSON catalog files against source/schema/odpc.yaml.
Use scripts/build_catalog.py to generate one ODPC catalog from a folder of standalone ProductReference, UseCase, BusinessObjective, Signal, metadata, ODPS product, or full catalog YAML files.
Use scripts/build_catalog.py --html to also generate a standalone browser-viewable catalog page; use --html-template to apply a custom editable HTML template.
Use scripts/check_agent_artifacts.py in CI or review workflows to detect drift between schema, catalog artifacts, examples, and llms.txt.
Use scripts/generate_catalog_artifacts.py after editing source/schema/odpc.yaml to regenerate source/schema/odpc.json; use --check in CI or review workflows.
Use scripts/explain_catalog.py to summarize an ODPC catalog file for humans or AI agents.
Install script dependencies with python -m pip install -r scripts/requirements-agent.txt.
Do not edit generated or derived artifacts without checking alignment across llms.txt, schema files, catalog artifacts, examples, and tests.
-->

| Script | Purpose |
|---|---|
| [`check_agent_artifacts.py`](https://github.com/Open-Data-Product-Initiative/odpc-v1.0/blob/main/scripts/check_agent_artifacts.py) | Checks schema alignment, example files, object JSONL records, and `llms.txt` references |
| [`generate_catalog_artifacts.py`](https://github.com/Open-Data-Product-Initiative/odpc-v1.0/blob/main/scripts/generate_catalog_artifacts.py) | Regenerates derived catalog artifacts such as `source/schema/odpc.json` from canonical source files; use `--check` to detect drift |
| [`build_catalog.py`](https://github.com/Open-Data-Product-Initiative/odpc-v1.0/blob/main/scripts/build_catalog.py) | Builds one ODPC catalog from a folder of standalone YAML or JSON fragments, ODPS product files, optional metadata files, and existing full catalog files; optionally renders browser-viewable HTML with `--html` and `--html-template` |
| [`search_objects.py`](https://github.com/Open-Data-Product-Initiative/odpc-v1.0/blob/main/scripts/search_objects.py) | Searches ODPC object records by keyword or exact object id; use `--json` for machine-readable results |
| [`validate_catalog.py`](https://github.com/Open-Data-Product-Initiative/odpc-v1.0/blob/main/scripts/validate_catalog.py) | Validates ODPC YAML or JSON catalog files against the ODPC schema |
| [`explain_catalog.py`](https://github.com/Open-Data-Product-Initiative/odpc-v1.0/blob/main/scripts/explain_catalog.py) | Summarizes an ODPC catalog file, including counts, ids, graph reference, and modeling hints |

The default HTML template is [`catalog.html`](https://github.com/Open-Data-Product-Initiative/odpc-v1.0/blob/main/source/catalog/templates/catalog.html). Copy and edit it when a generated catalog needs organization-specific branding, layout, or styling.

The Markdown tables in this specification are intended for human readers. The schema, JSONL, and YAML example files are intended for programmable use, automation, validation, AI retrieval, and catalog tooling.
