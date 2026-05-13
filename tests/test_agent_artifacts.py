import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"


def load_yaml(path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def assert_lang_string(value):
    assert isinstance(value, dict)
    assert isinstance(value.get("en"), str)
    assert value["en"].strip()


def assert_named_object(value, prefix):
    assert isinstance(value.get("id"), str)
    assert value["id"].startswith(prefix)
    assert_lang_string(value.get("name"))
    assert_lang_string(value.get("description"))


class AgentArtifactsTest(unittest.TestCase):
    def test_schema_uses_catalog_root_instead_of_product_root(self):
        schema = load_yaml(SOURCE / "schema" / "odpc.yaml")
        json_schema = json.loads((SOURCE / "schema" / "odpc.json").read_text(encoding="utf-8"))

        self.assertEqual(schema["required"], ["schema", "version", "catalog"])
        self.assertIn("catalog", schema["properties"])
        self.assertNotIn("product", schema["properties"])
        self.assertEqual(json_schema["required"], schema["required"])
        self.assertIn("catalog", json_schema["properties"])
        self.assertNotIn("product", json_schema["properties"])

        catalog_ref = schema["properties"]["catalog"]["$ref"].split("/")[-1]
        catalog = schema["$defs"][catalog_ref]
        self.assertEqual(catalog["required"], ["meta"])
        self.assertIn("meta", catalog["properties"])
        meta_ref = catalog["properties"]["meta"]["$ref"].split("/")[-1]
        meta = schema["$defs"][meta_ref]
        self.assertEqual(meta["required"], ["id", "name", "description"])
        self.assertIn("tags", meta["properties"])
        self.assertNotIn("tags", catalog["properties"])
        graph_reference = schema["$defs"]["GraphReference"]
        self.assertEqual(graph_reference["required"], ["standard", "version", "$ref"])
        self.assertIn("$ref", graph_reference["properties"])
        self.assertNotIn("uri", graph_reference["properties"])
        for collection in ["productReferences", "useCases", "businessObjectives", "signals"]:
            self.assertIn(collection, catalog["properties"])

    def test_examples_cover_minimal_full_and_each_core_object(self):
        expected = [
            "minimal.yaml",
            "full.yaml",
            "product-reference.yaml",
            "use-case.yaml",
            "business-objective-with-kpis.yaml",
            "signal.yaml",
        ]

        for filename in expected:
            self.assertTrue((SOURCE / "catalog" / "examples" / filename).is_file())

        minimal = load_yaml(SOURCE / "catalog" / "examples" / "minimal.yaml")
        self.assertEqual(minimal["schema"], "https://opendataproducts.org/odpc-v1.0/schema/odpc.yaml")
        self.assertEqual(minimal["version"], "1.0")
        assert_named_object(minimal["catalog"]["meta"], "CAT-")

        full = load_yaml(SOURCE / "catalog" / "examples" / "full.yaml")
        catalog = full["catalog"]
        assert_named_object(catalog["meta"], "CAT-")
        self.assertIn("tags", catalog["meta"])
        self.assertNotIn("tags", catalog)
        self.assertIn("$ref", catalog["meta"]["graph"])
        self.assertNotIn("uri", catalog["meta"]["graph"])
        assert_named_object(catalog["productReferences"][0], "DP-")
        assert_named_object(catalog["useCases"][0], "UC-")
        assert_named_object(catalog["businessObjectives"][0], "BO-")
        assert_named_object(catalog["signals"][0], "SIG-")

        product_reference = load_yaml(SOURCE / "catalog" / "examples" / "product-reference.yaml")["productReference"]
        assert_named_object(product_reference, "DP-")
        self.assertEqual(product_reference["productModel"]["standard"], "ODPS")
        self.assertIn("$ref", product_reference["productModel"])
        self.assertNotIn("uri", product_reference["productModel"])

    def test_product_model_uses_ref_for_odps_aligned_file_or_url_links(self):
        schema = load_yaml(SOURCE / "schema" / "odpc.yaml")
        product_model = schema["$defs"]["ProductModel"]

        self.assertEqual(product_model["required"], ["standard", "version", "format", "$ref"])
        self.assertIn("$ref", product_model["properties"])
        self.assertNotIn("uri", product_model["properties"])
        self.assertEqual(product_model["properties"]["$ref"]["type"], "string")

        use_case = load_yaml(SOURCE / "catalog" / "examples" / "use-case.yaml")["useCase"]
        assert_named_object(use_case, "UC-")
        self.assertTrue(use_case["dataNeeds"]["items"])

        objective = load_yaml(SOURCE / "catalog" / "examples" / "business-objective-with-kpis.yaml")["businessObjective"]
        assert_named_object(objective, "BO-")
        self.assertTrue(objective["kpis"][0]["id"].startswith("KPI-"))

        signal = load_yaml(SOURCE / "catalog" / "examples" / "signal.yaml")["signal"]
        assert_named_object(signal, "SIG-")
        self.assertIn(signal["source"]["origin"], {"internal", "external", "mixed"})

    def test_retrieval_jsonl_is_parseable_and_referenced(self):
        jsonl_path = SOURCE / "catalog" / "objects.jsonl"
        self.assertTrue(jsonl_path.is_file())

        records = [
            json.loads(line)
            for line in jsonl_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        ids = {record["id"] for record in records}
        self.assertEqual(ids, {"Catalog", "ProductReference", "UseCase", "BusinessObjective", "KPI", "Signal"})

        for record in records:
            self.assertTrue(record["definition"])
            self.assertIsInstance(record["requiredFields"], list)
            self.assertTrue(record["doUseFor"])
            self.assertTrue(record["doNotUseFor"])

        llms = (SOURCE / "llms.txt").read_text(encoding="utf-8")
        self.assertIn("/catalog/objects.jsonl", llms)


if __name__ == "__main__":
    unittest.main()
