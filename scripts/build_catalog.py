#!/usr/bin/env python
import argparse
import html
import json
import sys
from pathlib import Path

import yaml

from odpc_paths import DEFAULT_CATALOG_HTML_TEMPLATE, SCHEMA_YAML
from validate_catalog import NoDatesSafeLoader, load_schema


SCHEMA_URI = "https://opendataproducts.org/odpc-v1.0/schema/odpc.yaml"
OBJECT_COLLECTIONS = {
    "productReference": "productReferences",
    "useCase": "useCases",
    "businessObjective": "businessObjectives",
    "signal": "signals",
}
CATALOG_COLLECTIONS = tuple(OBJECT_COLLECTIONS.values())
METADATA_KEYS = ("metadata", "catalogMetadata")
HTML_PLACEHOLDERS = (
    "title",
    "catalog_header",
    "summary",
    "product_references",
    "use_cases",
    "business_objectives",
    "signals",
)


def load_document(path):
    with path.open(encoding="utf-8") as handle:
        if path.suffix.lower() == ".json":
            return json.load(handle)
        return yaml.load(handle, Loader=NoDatesSafeLoader)


def iter_input_files(input_dir, recursive=True):
    patterns = ("*.yaml", "*.yml", "*.json")
    paths = []
    for pattern in patterns:
        paths.extend(input_dir.rglob(pattern) if recursive else input_dir.glob(pattern))
    return sorted(path for path in paths if path.is_file())


def lang_string(value):
    if isinstance(value, dict):
        return value
    return {"en": value}


def default_metadata(args):
    catalog_id = args.id or "CAT-GENERATED"
    name = args.name or "Generated ODPC Catalog"
    description = args.description or "Generated from ODPC YAML fragments."
    return {
        "id": catalog_id,
        "name": lang_string(name),
        "description": lang_string(description),
    }


def append_items(target, collection, items):
    if isinstance(items, list):
        target[collection].extend(item for item in items if item is not None)


def as_lang_string(value, fallback):
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        return {"en": value}
    return {"en": fallback}


def product_reference_from_product(document, source_path, input_dir):
    product = document.get("product")
    if not isinstance(product, dict):
        return None

    product_id = product.get("productID") or product.get("id") or source_path.stem
    product_version = product.get("productVersion") or product.get("version") or document.get("version") or "1.0.0"
    reference_path = source_path.relative_to(input_dir).as_posix()
    product_format = "json" if source_path.suffix.lower() == ".json" else "yaml"

    return {
        "id": product.get("id") or product_id,
        "productID": product_id,
        "productVersion": str(product_version),
        "name": as_lang_string(product.get("name"), product_id),
        "description": as_lang_string(product.get("description"), f"Reference to {product_id}."),
        "productModel": {
            "standard": "ODPS",
            "version": str(document.get("version") or product.get("standardVersion") or "4.1"),
            "format": product_format,
            "$ref": reference_path,
        },
    }


def collect_document(document, source_path, input_dir, catalog, metadata_candidates, embedded_metadata_candidates):
    if not isinstance(document, dict):
        raise ValueError(f"{source_path}: expected a YAML or JSON object at the document root")

    if isinstance(document.get("catalog"), dict):
        nested_catalog = document["catalog"]
        metadata = nested_catalog.get("metadata")
        if isinstance(metadata, dict):
            embedded_metadata_candidates.append(metadata)
        for collection in CATALOG_COLLECTIONS:
            append_items(catalog, collection, nested_catalog.get(collection))
        return

    for metadata_key in METADATA_KEYS:
        metadata = document.get(metadata_key)
        if isinstance(metadata, dict):
            metadata_candidates.append(metadata)

    for object_key, collection in OBJECT_COLLECTIONS.items():
        item = document.get(object_key)
        if item is not None:
            catalog[collection].append(item)

    product_reference = product_reference_from_product(document, source_path, input_dir)
    if product_reference:
        catalog["productReferences"].append(product_reference)

    for collection in CATALOG_COLLECTIONS:
        append_items(catalog, collection, document.get(collection))


def build_catalog(input_dir, args):
    catalog = {collection: [] for collection in CATALOG_COLLECTIONS}
    metadata_candidates = []
    embedded_metadata_candidates = []

    for path in iter_input_files(input_dir, recursive=not args.no_recursive):
        if args.output and path.resolve() == args.output.resolve():
            continue
        document = load_document(path)
        collect_document(document, path, input_dir, catalog, metadata_candidates, embedded_metadata_candidates)

    if metadata_candidates:
        metadata = metadata_candidates[0]
    elif embedded_metadata_candidates:
        metadata = embedded_metadata_candidates[0]
    else:
        metadata = default_metadata(args)
    if args.id:
        metadata["id"] = args.id
    if args.name:
        metadata["name"] = lang_string(args.name)
    if args.description:
        metadata["description"] = lang_string(args.description)

    catalog = {key: value for key, value in catalog.items() if value}
    catalog["metadata"] = metadata

    return {
        "schema": SCHEMA_URI,
        "version": "1.0",
        "kind": "Catalog",
        "catalog": {"metadata": catalog.pop("metadata"), **catalog},
    }


def validate_document(document):
    try:
        import jsonschema
    except ModuleNotFoundError:
        return None

    schema = load_schema(SCHEMA_YAML)
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    return sorted(validator.iter_errors(document), key=lambda error: list(error.path))


def write_yaml(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=False), encoding="utf-8")


def text_value(value, fallback=""):
    if isinstance(value, dict):
        return str(value.get("en") or fallback)
    if value is None:
        return fallback
    return str(value)


def escaped_text(value, fallback=""):
    return html.escape(text_value(value, fallback))


def render_link(value):
    if not value:
        return ""
    escaped = html.escape(str(value), quote=True)
    return f'<a href="{escaped}">{escaped}</a>'


def render_tags(items):
    if not isinstance(items, list) or not items:
        return ""
    tags = "".join(f"<li>{html.escape(str(item))}</li>" for item in items)
    return f'<ul class="odp-tags">{tags}</ul>'


def render_card(item, fields):
    if not isinstance(item, dict):
        return ""

    name = escaped_text(item.get("name"), item.get("id", "(unnamed)"))
    description = escaped_text(item.get("description"))
    lines = [
        '<article class="odp-card">',
        f"<h3>{name}</h3>",
        f'<p class="odp-id">{escaped_text(item.get("id"))}</p>',
    ]
    if description:
        lines.append(f"<p>{description}</p>")

    facts = []
    for label, key in fields:
        value = item.get(key)
        if value:
            facts.append(f"<dt>{html.escape(label)}</dt><dd>{escaped_text(value)}</dd>")
    product_model = item.get("productModel")
    if isinstance(product_model, dict):
        facts.append(
            "<dt>Product model</dt>"
            f"<dd>{escaped_text(product_model.get('standard'))} "
            f"{escaped_text(product_model.get('version'))} "
            f"{render_link(product_model.get('$ref'))}</dd>"
        )
    if facts:
        lines.append(f'<dl class="odp-facts">{"".join(facts)}</dl>')

    tag_html = render_tags(item.get("tags"))
    if tag_html:
        lines.append(tag_html)

    lines.append("</article>")
    return "\n".join(lines)


def render_section(title, items, fields):
    if not isinstance(items, list) or not items:
        return f'<section class="odp-section"><h2>{html.escape(title)}</h2><p>No entries.</p></section>'

    cards = "\n".join(render_card(item, fields) for item in items)
    return f'<section class="odp-section"><h2>{html.escape(title)}</h2>{cards}</section>'


def render_catalog_header(document):
    catalog = document.get("catalog", {})
    metadata = catalog.get("metadata", {}) if isinstance(catalog, dict) else {}
    graph = metadata.get("graph") if isinstance(metadata, dict) else None
    lines = [
        '<header class="odp-header">',
        f"<h1>{escaped_text(metadata.get('name'), 'ODPC Catalog')}</h1>",
        f'<p class="odp-id">{escaped_text(metadata.get("id"))}</p>',
        f'<p class="odp-description">{escaped_text(metadata.get("description"))}</p>',
    ]
    if isinstance(graph, dict):
        lines.append(
            '<p class="odp-graph">'
            f"Graph: {escaped_text(graph.get('standard'))} {escaped_text(graph.get('version'))} "
            f"{render_link(graph.get('$ref'))}</p>"
        )
    lines.append("</header>")
    return "\n".join(lines)


def render_summary(document):
    catalog = document.get("catalog", {})
    counts = {
        "Product References": len(catalog.get("productReferences", [])),
        "Use Cases": len(catalog.get("useCases", [])),
        "Business Objectives": len(catalog.get("businessObjectives", [])),
        "Signals": len(catalog.get("signals", [])),
    }
    items = "".join(
        f'<li><span class="odp-count">{count}</span><span>{html.escape(label)}</span></li>'
        for label, count in counts.items()
    )
    return f'<section class="odp-summary"><h2>Summary</h2><ul>{items}</ul></section>'


def render_html_fragments(document):
    catalog = document.get("catalog", {})
    metadata = catalog.get("metadata", {}) if isinstance(catalog, dict) else {}
    return {
        "title": escaped_text(metadata.get("name"), "ODPC Catalog"),
        "catalog_header": render_catalog_header(document),
        "summary": render_summary(document),
        "product_references": render_section(
            "Product References",
            catalog.get("productReferences", []),
            [("Product ID", "productID"), ("Version", "productVersion"), ("Status", "status"), ("Visibility", "visibility")],
        ),
        "use_cases": render_section(
            "Use Cases",
            catalog.get("useCases", []),
            [("Status", "status"), ("Priority", "priority"), ("Decision", "decision"), ("Expected outcome", "expectedOutcome")],
        ),
        "business_objectives": render_section(
            "Business Objectives",
            catalog.get("businessObjectives", []),
            [("Status", "status"), ("Priority", "priority")],
        ),
        "signals": render_section(
            "Signals",
            catalog.get("signals", []),
            [("Type", "type"), ("Strength", "strength"), ("Confidence", "confidence"), ("Status", "status")],
        ),
    }


def render_html(document, template_path=DEFAULT_CATALOG_HTML_TEMPLATE):
    try:
        template = template_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"HTML template not found: {template_path}") from exc

    rendered = template
    fragments = render_html_fragments(document)
    for placeholder in HTML_PLACEHOLDERS:
        rendered = rendered.replace("{{ " + placeholder + " }}", fragments[placeholder])
    return rendered


def write_html(path, document, template_path=DEFAULT_CATALOG_HTML_TEMPLATE):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html(document, template_path), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build one ODPC catalog from a folder of ODPC YAML, YML, or JSON files.",
    )
    parser.add_argument("input_dir", help="Folder containing standalone ODPC objects or catalog YAML/JSON files")
    parser.add_argument("--output", "-o", required=True, help="Output catalog YAML path")
    parser.add_argument("--html", help="Optional output path for a standalone browser-viewable HTML catalog")
    parser.add_argument("--html-template", help="Optional HTML template path for --html output")
    parser.add_argument("--id", help="Catalog metadata id to use or override")
    parser.add_argument("--name", help="Catalog metadata name.en to use or override")
    parser.add_argument("--description", help="Catalog metadata description.en to use or override")
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only read files directly inside input_dir instead of scanning nested folders.",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Write the catalog without validating it against the ODPC schema.",
    )
    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir)
    args.output = Path(args.output)
    html_output = Path(args.html) if args.html else None
    html_template = Path(args.html_template) if args.html_template else DEFAULT_CATALOG_HTML_TEMPLATE

    if not input_dir.is_dir():
        print(f"Input folder not found: {input_dir}", file=sys.stderr)
        return 1

    try:
        document = build_catalog(input_dir, args)
        if not args.no_validate:
            errors = validate_document(document)
            if errors:
                print("Generated catalog is invalid:", file=sys.stderr)
                for error in errors:
                    location = ".".join(str(part) for part in error.path) or "<root>"
                    print(f"- {location}: {error.message}", file=sys.stderr)
                return 1
        write_yaml(args.output, document)
        if html_output:
            write_html(html_output, document, html_template)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    counts = document["catalog"]
    print(
        "Generated "
        f"{args.output} "
        f"(productReferences={len(counts.get('productReferences', []))}, "
        f"useCases={len(counts.get('useCases', []))}, "
        f"businessObjectives={len(counts.get('businessObjectives', []))}, "
        f"signals={len(counts.get('signals', []))})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
