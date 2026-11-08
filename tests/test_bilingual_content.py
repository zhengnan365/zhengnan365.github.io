import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.md"
PUBLICATIONS = ROOT / "_includes/publications.md"


class BilingualContentTests(unittest.TestCase):
    def test_page_sections_have_bilingual_headings_and_content(self):
        page = PAGE.read_text(encoding="utf-8")
        for section_id in (
            "about", "research", "patents", "projects", "students",
            "awards", "news", "contact",
        ):
            with self.subTest(section=section_id):
                start = page.index(f'id="{section_id}"')
                next_section = page.find('<section', start + 1)
                block = page[start:next_section if next_section != -1 else len(page)]
                self.assertRegex(block, r'<h2>\s*<span class="i18n-zh">[^<]+</span>\s*<span class="i18n-en">[^<]+</span>\s*</h2>')
                self.assertIn('class="i18n-zh"', block)
                self.assertIn('class="i18n-en"', block)

    def test_publication_heading_and_note_are_bilingual(self):
        publications = PUBLICATIONS.read_text(encoding="utf-8")
        self.assertRegex(publications, r'<h2 class="pub-section-title">\s*<span class="i18n-zh">论文</span>\s*<span class="i18n-en">Publications</span>')
        self.assertRegex(publications, r'<p class="section-note">\s*<span class="i18n-zh">[^<]+</span>\s*<span class="i18n-en">[^<]+</span>\s*</p>')
        item = (ROOT / "_includes/publication-item.html").read_text(encoding="utf-8")
        self.assertIn("{{ link.title | escape }}", item)
        self.assertIn("{{ link.display_authors }}", item)
        self.assertIn("{{ link.venue | escape }}", item)

    def test_yaml_collections_and_rendering_have_both_languages(self):
        page = PAGE.read_text(encoding="utf-8")
        fields = {
            "patents": "text",
            "projects": "title",
            "awards": "title",
            "news": "text",
        }
        for collection, field in fields.items():
            with self.subTest(collection=collection):
                records = yaml.safe_load((ROOT / f"_data/{collection}.yml").read_text(encoding="utf-8"))
                self.assertTrue(records)
                for record in records:
                    self.assertTrue(record[f"{field}_zh"])
                    self.assertTrue(record[f"{field}_en"])
                section = re.search(
                    rf'<section\b[^>]*\bid="{collection}"[^>]*>(.*?)</section>',
                    page,
                    re.DOTALL,
                )
                self.assertIsNotNone(section)
                block = section.group(1)
                self.assertIn(f"site.data.{collection}", block)
                self.assertIn(f"{{{{ item.{field}_zh }}}}", block)
                self.assertIn(f"{{{{ item.{field}_en }}}}", block)
        projects = yaml.safe_load((ROOT / "_data/projects.yml").read_text(encoding="utf-8"))
        for project in projects:
            self.assertTrue(project["role_zh"])
            self.assertTrue(project["role_en"])
            self.assertTrue(project["amount_zh"])
            self.assertTrue(project["amount_en"])
        projects_block = re.search(
            r'<section\b[^>]*\bid="projects"[^>]*>(.*?)</section>',
            page,
            re.DOTALL,
        ).group(1)
        for field in ("role_zh", "role_en", "amount_zh", "amount_en"):
            self.assertIn("{{ item." + field + " }}", projects_block)

    def test_project_translations_retain_research_mechanisms_and_control(self):
        projects = yaml.safe_load((ROOT / "_data/projects.yml").read_text(encoding="utf-8"))
        first = projects[0]["title_en"].lower()
        second = projects[1]["title_en"].lower()
        self.assertIn("coupling mechanisms", first)
        self.assertIn("coordinated control", first)
        self.assertIn("integration mechanisms", second)
        self.assertIn("control optimization", second)


if __name__ == "__main__":
    unittest.main()
