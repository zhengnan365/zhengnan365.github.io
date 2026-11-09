import re
import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.md"
PUBLICATIONS = ROOT / "_includes/publications.md"


class BilingualContentTests(unittest.TestCase):
    def test_profile_and_navigation_brand_follow_page_language(self):
        layout = (ROOT / "_layouts/homepage.html").read_text(encoding="utf-8")
        navigation = (ROOT / "_includes/topnav.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="zh-CN" data-lang="zh"', layout)
        self.assertRegex(layout, r'<h1>\s*<span class="i18n-zh">{{ site.title_zh }}</span>\s*<span class="i18n-en">{{ site.title }}</span>\s*</h1>')
        self.assertRegex(layout, r'<position[^>]*>\s*<span class="i18n-zh">{{ site.position_zh }}</span>\s*<span class="i18n-en">{{ site.position }}</span>\s*</position>')
        self.assertRegex(layout, r'<autocolor>\s*<span class="i18n-zh">{{ site.affiliation_zh }}</span>\s*<span class="i18n-en">{{ site.affiliation }}</span>\s*</autocolor>')
        self.assertRegex(navigation, r'<a class="topnav-brand"[^>]*>\s*<span class="i18n-zh">{{ site.title_zh }}</span>\s*<span class="i18n-en">{{ site.title }}</span>\s*</a>')

    def test_page_sections_have_bilingual_headings_and_content(self):
        page = PAGE.read_text(encoding="utf-8")
        for section_id in (
            "about", "research", "patents", "projects", "students",
            "awards", "teaching", "opensource", "contact",
        ):
            with self.subTest(section=section_id):
                start = page.index(f'id="{section_id}"')
                next_section = page.find('<section', start + 1)
                block = page[start:next_section if next_section != -1 else len(page)]
                if section_id == "patents":
                    self.assertRegex(block, r'<h2>\s*<span class="i18n-zh">专利</span>\s*<span class="i18n-en">Patents</span>\s*<small class="pub-total">')
                else:
                    self.assertRegex(block, r'<h2>\s*<span class="i18n-zh">[^<]+</span>\s*<span class="i18n-en">[^<]+</span>\s*</h2>')
                self.assertIn('class="i18n-zh"', block)
                self.assertIn('class="i18n-en"', block)

    def test_publication_heading_and_note_are_bilingual(self):
        publications = PUBLICATIONS.read_text(encoding="utf-8")
        self.assertRegex(publications, r'<h2 class="pub-section-title">\s*<span class="i18n-zh">论文</span>\s*<span class="i18n-en">Publications</span>')
        self.assertIn('class="section-note publication-source"', publications)
        self.assertIn('href="https://openalex.org/A5001145059"', publications)
        self.assertIn('class="older-publications"', publications)
        self.assertIn('site.data.publications.main.size', publications)
        item = (ROOT / "_includes/publication-item.html").read_text(encoding="utf-8")
        self.assertIn("{{ link.title | escape }}", item)
        self.assertIn("{{ link.display_authors }}", item)
        self.assertIn("{{ link.venue | escape }}", item)

    def test_navigation_labels_match_page_sections_and_single_divider(self):
        page = PAGE.read_text(encoding="utf-8")
        navigation = yaml.safe_load((ROOT / "_data/navigation.yml").read_text(encoding="utf-8"))["main"]
        expected = {
            "#about": "个人简介",
            "#research": "研究方向",
            "#projects": "项目承担",
            "#publications": "论文",
            "#awards": "获奖",
            "#patents": "专利",
            "#teaching": "教学",
            "#students": "指导学生",
            "#opensource": "开源软件",
            "#contact": "联系",
        }
        self.assertEqual({item["url"]: item["title_zh"] for item in navigation}, expected)
        self.assertIn('<section id="awards" class="section-divider">', page)
        self.assertEqual(page.count('class="section-divider"'), 1)

    def test_teaching_courses_are_grouped_by_semester_without_codes(self):
        page = PAGE.read_text(encoding="utf-8")
        teaching = page.split('<section id="teaching">', 1)[1].split('</section>', 1)[0]
        fifth, sixth = teaching.split('第六学期', 1)
        self.assertIn('第五学期', fifth)
        for title in ('计算机辅助设计', '综合能源高效利用技术'):
            self.assertIn(title, fifth)
        for title in ('光伏系统设计', '能源互联网技术与应用-人工智能+', '新能源综合项目创新实践'):
            self.assertIn(title, sixth)
        self.assertNotRegex(teaching, r'\b(?:21164038|25163018|25165026|25167014)\b')

    def test_yaml_collections_and_rendering_have_both_languages(self):
        page = PAGE.read_text(encoding="utf-8")
        fields = {
            "patents": "title",
            "projects": "title",
            "awards": "title",
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
        software = yaml.safe_load((ROOT / "_data/opensource.yml").read_text(encoding="utf-8"))
        self.assertTrue(software)
        self.assertTrue(all(item["name"] and item["url"] and item["description_zh"] and item["description_en"] for item in software))
        self.assertIn("site.data.opensource", page)

    def test_project_translations_retain_research_mechanisms_and_control(self):
        projects = yaml.safe_load((ROOT / "_data/projects.yml").read_text(encoding="utf-8"))
        first = projects[0]["title_en"].lower()
        second = projects[1]["title_en"].lower()
        self.assertIn("coupling mechanisms", first)
        self.assertIn("coordinated control", first)
        self.assertIn("integration mechanisms", second)
        self.assertIn("control optimization", second)

    def test_teaching_precedes_open_source_and_project_metadata_is_amount_first(self):
        page = PAGE.read_text(encoding="utf-8")
        navigation = (ROOT / "_data/navigation.yml").read_text(encoding="utf-8")
        self.assertLess(page.index('id="teaching"'), page.index('id="students"'))
        self.assertLess(page.index('id="students"'), page.index('id="opensource"'))
        self.assertLess(page.index('id="patents"'), page.index('id="awards"'))
        self.assertLess(page.index('id="awards"'), page.index('id="teaching"'))
        self.assertLess(navigation.index('url: "#teaching"'), navigation.index('url: "#students"'))
        self.assertLess(navigation.index('url: "#patents"'), navigation.index('url: "#awards"'))
        self.assertLess(navigation.index('url: "#awards"'), navigation.index('url: "#teaching"'))
        self.assertLess(navigation.index('url: "#students"'), navigation.index('url: "#opensource"'))
        self.assertIn('<div class="patent-list compact-list">', page)
        self.assertIn('· {{ item.amount_zh }} · {{ item.role_zh }}', page)
        self.assertIn('· {{ item.amount_en }} · {{ item.role_en }}', page)
        styles = (ROOT / "assets/css/site-overrides.css").read_text(encoding="utf-8")
        self.assertIn('.project h3 { display: inline;', styles)
        self.assertIn('.project p { display: inline;', styles)

    def test_patents_show_recent_records_first_with_author_emphasis(self):
        page = PAGE.read_text(encoding="utf-8")
        patents = yaml.safe_load((ROOT / "_data/patents.yml").read_text(encoding="utf-8"))
        dates = [item["display_date"] for item in patents]
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertTrue(all(item["status_zh"] != "已失效" for item in patents))
        self.assertIn('<strong>{{ inventor }}</strong>', page)
        section = page.split('<section id="patents"', 1)[1].split('</section>', 1)[0]
        self.assertIn('class="publication-badges"', section)
        self.assertNotIn('patent-source', section)

    def test_main_journals_have_curated_metrics_in_generated_feed(self):
        records = json.loads((ROOT / "assets/data/site-data.json").read_text(encoding="utf-8"))["publications"]
        covered = {"Energy", "Energy Conversion and Management", "Renewable Energy",
                   "Applied Energy", "Applied Thermal Engineering", "Journal of Energy Storage"}
        self.assertTrue(covered.issubset({item["venue"] for item in records}))
        for item in records:
            if item["venue"] in covered:
                with self.subTest(venue=item["venue"], title=item["title"]):
                    self.assertEqual(item["metrics"]["metric_year"], 2025)
                    self.assertTrue(item["metrics"]["impact_factor"])
                    self.assertTrue(item["metrics"]["cas_label_zh"])
                    self.assertTrue(item["metrics"]["jcr_quartile"])


if __name__ == "__main__":
    unittest.main()
