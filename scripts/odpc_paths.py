from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
SCHEMA_YAML = SOURCE / "schema" / "odpc.yaml"
SCHEMA_JSON = SOURCE / "schema" / "odpc.json"
OBJECTS_JSONL = SOURCE / "objects" / "odpc-objects.jsonl"
LLMS_TXT = SOURCE / "llms.txt"
EXAMPLES_DIR = SOURCE / "examples"

