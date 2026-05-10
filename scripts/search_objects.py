#!/usr/bin/env python3
import argparse
import json
import sys

from odpc_paths import OBJECTS_JSONL


def load_records(path=OBJECTS_JSONL):
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid JSONL: {exc}") from exc
    return records


def searchable_text(record):
    values = []
    for value in record.values():
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        else:
            values.append(str(value))
    return " ".join(values).lower()


def search(records, query=None, object_id=None):
    if object_id:
        wanted = object_id.lower()
        return [record for record in records if record.get("id", "").lower() == wanted]

    terms = [term.lower() for term in (query or "").split() if term.strip()]
    if not terms:
        return records

    results = []
    for record in records:
        text = searchable_text(record)
        if all(term in text for term in terms):
            results.append(record)
    return results


def render_text(records):
    if not records:
        return "No matching ODPC objects found.\n"

    sections = []
    for record in records:
        sections.append(
            "\n".join(
                [
                    f"{record['id']}",
                    f"  Definition: {record['definition']}",
                    f"  Required fields: {', '.join(record['requiredFields']) or '(none)'}",
                    f"  Use for: {', '.join(record['doUseFor'])}",
                    f"  Do not use for: {', '.join(record['doNotUseFor'])}",
                    f"  Example: {record['exampleFile']}",
                ]
            )
        )
    return "\n\n".join(sections) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Search ODPC agent-friendly object records.",
    )
    parser.add_argument("query", nargs="?", help="Keyword query, for example: demand")
    parser.add_argument("--id", dest="object_id", help="Return one object by id, for example: ProductReference")
    parser.add_argument("--json", action="store_true", help="Emit JSON array output")
    args = parser.parse_args(argv)

    records = search(load_records(), query=args.query, object_id=args.object_id)
    if args.json:
        print(json.dumps(records, indent=2))
    else:
        sys.stdout.write(render_text(records))
    return 0 if records else 1


if __name__ == "__main__":
    raise SystemExit(main())

