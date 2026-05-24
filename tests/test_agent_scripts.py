import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


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
        result = run_script("scripts/validate_catalog.py", "source/catalog/examples/minimal.yaml")

        if result.returncode == 2:
            self.assertIn("jsonschema", result.stderr)
        else:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("valid", result.stdout.lower())

    def test_generate_catalog_artifacts_check_passes(self):
        result = run_script("scripts/generate_catalog_artifacts.py", "--check")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("up to date", result.stdout.lower())

    def test_explain_catalog_summarizes_full_example(self):
        result = run_script("scripts/explain_catalog.py", "source/catalog/examples/full.yaml")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Urban Mobility Data Product Catalog", result.stdout)
        self.assertIn("Product references: 1", result.stdout)
        self.assertIn("Use cases: 1", result.stdout)
        self.assertIn("Business objectives: 1", result.stdout)
        self.assertIn("Signals: 1", result.stdout)

    def test_build_catalog_combines_standalone_yaml_fragments(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_dir = Path(tmp_dir)
            output_path = input_dir / "catalog.yaml"
            for example in (
                "product-reference.yaml",
                "use-case.yaml",
                "business-objective-with-kpis.yaml",
                "signal.yaml",
            ):
                source = ROOT / "source" / "catalog" / "examples" / example
                (input_dir / example).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            result = run_script(
                "scripts/build_catalog.py",
                str(input_dir),
                "--id",
                "CAT-GENERATED",
                "--name",
                "Generated Catalog",
                "--description",
                "Generated from standalone YAML fragments.",
                "--output",
                str(output_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            generated = yaml.safe_load(output_path.read_text(encoding="utf-8"))
            self.assertEqual(generated["kind"], "Catalog")
            self.assertEqual(generated["catalog"]["metadata"]["id"], "CAT-GENERATED")
            self.assertEqual(len(generated["catalog"]["productReferences"]), 1)
            self.assertEqual(len(generated["catalog"]["useCases"]), 1)
            self.assertEqual(len(generated["catalog"]["businessObjectives"]), 1)
            self.assertEqual(len(generated["catalog"]["signals"]), 1)

    def test_build_catalog_uses_metadata_file_and_full_catalog_inputs(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_dir = Path(tmp_dir)
            output_path = input_dir / "nested" / "catalog.yaml"
            (input_dir / "metadata.yaml").write_text(
                "\n".join(
                    [
                        "metadata:",
                        "  id: CAT-META",
                        "  name:",
                        "    en: Metadata File Catalog",
                        "  description:",
                        "    en: Metadata from the input folder.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            full_example = ROOT / "source" / "catalog" / "examples" / "full.yaml"
            (input_dir / "full.yaml").write_text(full_example.read_text(encoding="utf-8"), encoding="utf-8")

            result = run_script("scripts/build_catalog.py", str(input_dir), "--output", str(output_path))

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            generated = yaml.safe_load(output_path.read_text(encoding="utf-8"))
            self.assertEqual(generated["catalog"]["metadata"]["id"], "CAT-META")
            self.assertEqual(generated["catalog"]["metadata"]["name"]["en"], "Metadata File Catalog")
            self.assertEqual(len(generated["catalog"]["productReferences"]), 1)
            self.assertEqual(len(generated["catalog"]["useCases"]), 1)
            self.assertEqual(len(generated["catalog"]["businessObjectives"]), 1)
            self.assertEqual(len(generated["catalog"]["signals"]), 1)

    def test_build_catalog_turns_product_yaml_into_product_reference(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_dir = Path(tmp_dir)
            product_dir = input_dir / "products"
            product_dir.mkdir()
            (product_dir / "weather-product.yaml").write_text(
                "\n".join(
                    [
                        "schema: https://opendataproducts.org/odps-v4.1/schema/odps.yaml",
                        "version: \"4.1\"",
                        "product:",
                        "  productID: weather-observations",
                        "  version: \"2.0.0\"",
                        "  name:",
                        "    en: Weather Observations",
                        "  description:",
                        "    en: Weather observation data product.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            output_path = input_dir / "catalog.yaml"

            result = run_script(
                "scripts/build_catalog.py",
                str(input_dir),
                "--id",
                "CAT-PRODUCTS",
                "--name",
                "Product Catalog",
                "--description",
                "Generated from product files.",
                "--output",
                str(output_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            generated = yaml.safe_load(output_path.read_text(encoding="utf-8"))
            references = generated["catalog"]["productReferences"]
            self.assertEqual(len(references), 1)
            self.assertEqual(references[0]["productID"], "weather-observations")
            self.assertEqual(references[0]["productVersion"], "2.0.0")
            self.assertEqual(references[0]["productModel"]["standard"], "ODPS")
            self.assertEqual(references[0]["productModel"]["$ref"], "products/weather-product.yaml")

    def test_build_catalog_can_render_default_html_view(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_dir = Path(tmp_dir)
            output_path = input_dir / "catalog.yaml"
            html_path = input_dir / "catalog.html"
            source = ROOT / "source" / "catalog" / "examples" / "use-case.yaml"
            (input_dir / "use-case.yaml").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            result = run_script(
                "scripts/build_catalog.py",
                str(input_dir),
                "--id",
                "CAT-HTML",
                "--name",
                "HTML Catalog",
                "--description",
                "Generated browser view.",
                "--output",
                str(output_path),
                "--html",
                str(html_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            html = html_path.read_text(encoding="utf-8")
            self.assertIn("<!doctype html>", html)
            self.assertIn("HTML Catalog", html)
            self.assertIn("CAT-HTML", html)
            self.assertIn("Event Demand Forecasting", html)
            self.assertIn("Use Cases", html)

    def test_build_catalog_can_render_custom_html_template(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_dir = Path(tmp_dir)
            output_path = input_dir / "catalog.yaml"
            html_path = input_dir / "custom.html"
            template_path = input_dir / "template.html"
            source = ROOT / "source" / "catalog" / "examples" / "signal.yaml"
            (input_dir / "signal.yaml").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            template_path.write_text(
                "<html><head><title>{{ title }}</title></head><body>"
                "<main class='custom'>{{ catalog_header }}{{ signals }}</main>"
                "</body></html>\n",
                encoding="utf-8",
            )

            result = run_script(
                "scripts/build_catalog.py",
                str(input_dir),
                "--id",
                "CAT-CUSTOM",
                "--name",
                "Custom Catalog",
                "--description",
                "Custom browser view.",
                "--output",
                str(output_path),
                "--html",
                str(html_path),
                "--html-template",
                str(template_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            html = html_path.read_text(encoding="utf-8")
            self.assertIn("<main class='custom'>", html)
            self.assertIn("<title>Custom Catalog</title>", html)
            self.assertIn("Increasing Event Demand", html)
            self.assertNotIn("{{ signals }}", html)


if __name__ == "__main__":
    unittest.main()
