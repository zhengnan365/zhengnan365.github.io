import json
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import sync_publications


class SyncPublicationTests(unittest.TestCase):
    def test_empty_fetch_does_not_replace_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            yaml_path = root / "publications.yml"
            json_path = root / "site-data.json"
            yaml_path.write_text("main:\n- title: Existing\n", encoding="utf-8")
            json_path.write_text('{"publications":[{"title":"Existing"}]}', encoding="utf-8")
            with self.assertRaises(RuntimeError):
                sync_publications.build_records([], {}, {})
            self.assertIn("Existing", yaml_path.read_text(encoding="utf-8"))
            self.assertIn("Existing", json_path.read_text(encoding="utf-8"))

    def test_generated_yaml_and_json_share_records(self):
        records = [{"stable_id": "10.1/example", "title": "Example", "year": 2025}]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sync_publications.write_outputs(records, root)
            yaml_records = yaml.safe_load(
                (root / "_data/publications.yml").read_text(encoding="utf-8")
            )["main"]
            json_records = json.loads(
                (root / "assets/data/site-data.json").read_text(encoding="utf-8")
            )["publications"]
            self.assertEqual(yaml_records, json_records)

    def test_generated_at_is_preserved_when_records_are_unchanged(self):
        records = [{"stable_id": "10.1/example", "title": "Example", "year": 2025}]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sync_publications.write_outputs(records, root)
            json_path = root / "assets/data/site-data.json"
            original = json.loads(json_path.read_text(encoding="utf-8"))
            sync_publications.write_outputs(records, root)
            updated = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["generated_at"], original["generated_at"])

    def test_duplicate_stable_ids_are_written_once(self):
        works = [
            {
                "id": "https://openalex.org/W1",
                "doi": "https://doi.org/10.1234/DUPLICATE",
                "title": "First",
                "publication_year": 2024,
                "publication_date": "2024-01-01",
                "type": "article",
                "authorships": [],
                "primary_location": {"source": {"display_name": "Journal"}},
            },
            {
                "id": "https://openalex.org/W2",
                "doi": "10.1234/duplicate",
                "title": "Second",
                "publication_year": 2025,
                "publication_date": "2025-01-01",
                "type": "article",
                "authorships": [],
                "primary_location": {"source": {"display_name": "Journal"}},
            },
        ]
        records = sync_publications.build_records(works, {}, {})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "Second")


if __name__ == "__main__":
    unittest.main()
