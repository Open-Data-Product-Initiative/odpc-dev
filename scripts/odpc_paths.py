from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
SCHEMA_YAML = SOURCE / "schema" / "odpc.yaml"
SCHEMA_JSON = SOURCE / "schema" / "odpc.json"
CATALOG_DIR = SOURCE / "catalog"
OBJECTS_JSONL = CATALOG_DIR / "objects.jsonl"
LLMS_TXT = SOURCE / "llms.txt"
EXAMPLES_DIR = CATALOG_DIR / "examples"
TEMPLATES_DIR = CATALOG_DIR / "templates"
DEFAULT_CATALOG_HTML_TEMPLATE = TEMPLATES_DIR / "catalog.html"
