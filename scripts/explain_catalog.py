#!/usr/bin/env python
import argparse
import json
from pathlib import Path

import yaml


class NoDatesSafeLoader(yaml.SafeLoader):
    pass


for first_char, resolvers in list(NoDatesSafeLoader.yaml_implicit_resolvers.items()):
    NoDatesSafeLoader.yaml_implicit_resolvers[first_char] = [
        (tag, regexp)
        for tag, regexp in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]


def load_catalog(path):
    with path.open(encoding="utf-8") as handle:
        if path.suffix.lower() == ".json":
            return json.load(handle)
        return yaml.load(handle, Loader=NoDatesSafeLoader)


def lang_en(value, fallback="(unnamed)"):
    if isinstance(value, dict):
        return value.get("en") or fallback
    if isinstance(value, str):
        return value
    return fallback


def count_items(catalog, key):
    value = catalog.get(key, [])
    return len(value) if isinstance(value, list) else 0


def collect_ids(items):
    if not isinstance(items, list):
        return []
    return [item.get("id") for item in items if isinstance(item, dict) and item.get("id")]


def render_summary(document, path):
    catalog = document.get("catalog", {}) if isinstance(document, dict) else {}
    meta = catalog.get("meta", {}) if isinstance(catalog, dict) else {}
    lines = [
        f"File: {path}",
        f"Schema: {document.get('schema', '(missing)') if isinstance(document, dict) else '(missing)'}",
        f"ODPC version: {document.get('version', '(missing)') if isinstance(document, dict) else '(missing)'}",
        f"Catalog id: {meta.get('id', '(missing)')}",
        f"Catalog name: {lang_en(meta.get('name'))}",
        f"Status: {meta.get('status', '(not set)')}",
        f"Product references: {count_items(catalog, 'productReferences')}",
        f"Use cases: {count_items(catalog, 'useCases')}",
        f"Business objectives: {count_items(catalog, 'businessObjectives')}",
        f"Signals: {count_items(catalog, 'signals')}",
    ]

    graph = meta.get("graph")
    if isinstance(graph, dict):
        lines.append(f"Graph: {graph.get('standard', '(unknown)')} {graph.get('version', '')} {graph.get('$ref', '')}".strip())
    else:
        lines.append("Graph: (not set)")

    ids = {
        "Product reference ids": collect_ids(catalog.get("productReferences", [])),
        "Use case ids": collect_ids(catalog.get("useCases", [])),
        "Business objective ids": collect_ids(catalog.get("businessObjectives", [])),
        "Signal ids": collect_ids(catalog.get("signals", [])),
    }
    for label, values in ids.items():
        if values:
            lines.append(f"{label}: {', '.join(values)}")

    hints = []
    if count_items(catalog, "productReferences") == 0:
        hints.append("No productReferences found; add ProductReference objects when cataloging data products.")
    if graph is None:
        hints.append("No graph reference found; use Catalog.meta.graph when relationships are implemented in ODPG or another graph standard.")
    if hints:
        lines.append("Hints:")
        lines.extend(f"- {hint}" for hint in hints)

    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Explain an ODPC catalog file for humans and AI agents.")
    parser.add_argument("catalog", help="Path to an ODPC YAML or JSON catalog file")
    args = parser.parse_args(argv)

    path = Path(args.catalog)
    try:
        document = load_catalog(path)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return 1
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Parse error: {exc}")
        return 1

    print(render_summary(document, path), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
