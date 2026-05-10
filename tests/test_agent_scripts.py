import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(*args):
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class AgentScriptsTest(unittest.TestCase):
    def test_check_agent_artifacts_script_passes(self):
        result = run_script("scripts/check_agent_artifacts.py")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("OK", result.stdout)

    def test_search_objects_returns_json_results(self):
        result = run_script("scripts/search_objects.py", "demand", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(result.stdout)
        ids = {record["id"] for record in records}
        self.assertIn("UseCase", ids)
        self.assertIn("Signal", ids)

    def test_search_objects_can_show_one_object(self):
        result = run_script("scripts/search_objects.py", "--id", "ProductReference")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ProductReference", result.stdout)
        self.assertIn("productModel", result.stdout)

    def test_validate_catalog_accepts_minimal_example_or_reports_missing_dependency(self):
        result = run_script("scripts/validate_catalog.py", "source/examples/minimal-catalog.yaml")

        if result.returncode == 2:
            self.assertIn("jsonschema", result.stderr)
        else:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("valid", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
