#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

import yaml

from odpc_paths import SCHEMA_YAML


class NoDatesSafeLoader(yaml.SafeLoader):
    pass


for first_char, resolvers in list(NoDatesSafeLoader.yaml_implicit_resolvers.items()):
    NoDatesSafeLoader.yaml_implicit_resolvers[first_char] = [
        (tag, regexp)
        for tag, regexp in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]


def load_data(path):
    suffix = path.suffix.lower()
    with path.open(encoding="utf-8") as handle:
        if suffix == ".json":
            return json.load(handle)
        return yaml.load(handle, Loader=NoDatesSafeLoader)


def load_schema(path=SCHEMA_YAML):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate an ODPC catalog file against the ODPC schema.")
    parser.add_argument("catalog", help="Path to an ODPC YAML or JSON catalog file")
    parser.add_argument("--schema", default=str(SCHEMA_YAML), help="Schema path. Defaults to source/schema/odpc.yaml")
    args = parser.parse_args(argv)

    try:
        import jsonschema
    except ModuleNotFoundError:
        print(
            "Missing dependency: jsonschema. Install agent tool dependencies with "
            "`python3 -m pip install -r scripts/requirements-agent.txt`.",
            file=sys.stderr,
        )
        return 2

    catalog_path = Path(args.catalog)
    schema_path = Path(args.schema)

    try:
        catalog = load_data(catalog_path)
        schema = load_schema(schema_path)
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(catalog), key=lambda error: list(error.path))
    except FileNotFoundError as exc:
        print(f"File not found: {exc.filename}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1
    except jsonschema.SchemaError as exc:
        print(f"Invalid ODPC schema: {exc.message}", file=sys.stderr)
        return 1

    if errors:
        print(f"{catalog_path}: invalid ODPC catalog", file=sys.stderr)
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            print(f"- {location}: {error.message}", file=sys.stderr)
        return 1

    print(f"{catalog_path}: valid ODPC catalog")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
