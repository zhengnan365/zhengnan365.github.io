import json
import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

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
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            records = sync_publications.build_records(works, {}, {})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "Second")
        self.assertIn("duplicate publication stable_id 10.1234/duplicate", stderr.getvalue())

    def test_batch_write_rolls_back_when_second_replace_fails(self):
        records = [{"stable_id": "10.1/example", "title": "New", "year": 2025}]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            yaml_path = root / "_data/publications.yml"
            json_path = root / "assets/data/site-data.json"
            yaml_path.parent.mkdir(parents=True)
            json_path.parent.mkdir(parents=True)
            yaml_path.write_text("main:\n- title: Old\n", encoding="utf-8")
            json_path.write_text('{"publications":[{"title":"Old"}]}', encoding="utf-8")
            real_replace = sync_publications.os.replace
            failed = False

            def replace_once_then_fail(source, destination):
                nonlocal failed
                if Path(destination).name == "site-data.json" and not failed:
                    failed = True
                    raise OSError("simulated second replacement failure")
                return real_replace(source, destination)

            with patch.object(sync_publications.os, "replace", side_effect=replace_once_then_fail):
                with self.assertRaises(OSError):
                    sync_publications.write_outputs(records, root)
            self.assertIn("Old", yaml_path.read_text(encoding="utf-8"))
            self.assertIn("Old", json_path.read_text(encoding="utf-8"))

    def test_overrides_keep_precedence_over_derived_fields(self):
        work = {
            "id": "https://openalex.org/W1",
            "doi": "https://doi.org/10.1234/example",
            "title": "Example",
            "publication_year": 2025,
            "type": "article",
            "authorships": [],
            "primary_location": {"source": {"display_name": "Journal"}},
            "open_access": {"is_oa": False},
            "best_oa_location": {"pdf_url": "https://example.test/derived.pdf"},
        }
        record = sync_publications.normalize(
            work,
            {
                "10.1234/example": {
                    "url": "https://example.test/manual",
                    "conference": "Manual venue",
                    "pdf": "https://example.test/manual.pdf",
                    "open_access": True,
                }
            },
            {},
        )
        self.assertEqual(record["url"], "https://example.test/manual")
        self.assertEqual(record["conference"], "Manual venue")
        self.assertEqual(record["pdf"], "https://example.test/manual.pdf")
        self.assertTrue(record["open_access"])


if __name__ == "__main__":
    unittest.main()
