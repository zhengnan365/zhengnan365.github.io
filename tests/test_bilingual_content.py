import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.md"
INCLUDES = ROOT / "_includes" / "sections"


def load_yaml(name):
    return yaml.safe_load((ROOT / "_data" / name).read_text(encoding="utf-8"))


def template(name):
    return (INCLUDES / f"{name}.html").read_text(encoding="utf-8")


class BilingualContentTests(unittest.TestCase):
    def test_profile_and_navigation_brand_follow_page_language(self):
        layout = (ROOT / "_layouts/homepage.html").read_text(encoding="utf-8")
        navigation = (ROOT / "_includes/topnav.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="zh-CN" data-lang="zh"', layout)
        self.assertRegex(layout, r'<h1>\s*<span class="i18n-zh">{{ site.title_zh }}</span>\s*<span class="i18n-en">{{ site.title }}</span>\s*</h1>')
        self.assertRegex(layout, r'<position[^>]*>\s*<span class="i18n-zh">{{ site.position_zh }}</span>\s*<span class="i18n-en">{{ site.position }}</span>\s*</position>')
        self.assertRegex(layout, r'<autocolor>\s*<span class="i18n-zh">{{ site.affiliation_zh }}</span>\s*<span class="i18n-en">{{ site.affiliation }}</span>\s*</autocolor>')
        self.assertRegex(navigation, r'<a class="topnav-brand"[^>]*>\s*<span class="i18n-zh">{{ site.title_zh }}</span>\s*<span class="i18n-en">{{ site.title }}</span>\s*</a>')

    def test_index_is_small_navigation_dispatcher(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertLess(len(page), 1600)
        self.assertIn("site.data.navigation.main", page)
        for key in ("about", "research", "projects", "publications", "patents", "awards", "teaching", "students", "opensource", "contact", "news"):
            self.assertIn(f"include sections/{key}.html", page)

    def test_navigation_entries_have_bilingual_section_templates(self):
        navigation = load_yaml("navigation.yml")["main"]
        expected = {
            "#about": "个人简介",
            "#research": "研究方向",
            "#projects": "项目承担",
            "#publications": "论文",
            "#patents": "专利",
            "#awards": "获奖",
            "#teaching": "教学",
            "#students": "指导学生",
            "#opensource": "开源软件",
            "#contact": "联系",
            "#news": "新闻动态",
        }
        self.assertEqual({item["url"] for item in navigation}, set(expected))
        self.assertEqual(len({item["key"] for item in navigation}), len(navigation))
        for item in navigation:
            self.assertIsInstance(item["enabled"], bool)
            self.assertTrue(item["title_zh"])
            self.assertTrue(item["title_en"])
            self.assertEqual(item["url"], f'#{item["key"]}')
            block = template(item["template"])
            self.assertIn(f'id="{item["key"]}"', block)
            if item["key"] not in ("publications", "patents"):
                self.assertRegex(block, r'<h2>\s*<span class="i18n-zh">[^<]+</span>\s*<span class="i18n-en">[^<]+</span>\s*</h2>')

    def test_navigation_and_page_use_the_same_section_switch(self):
        page = PAGE.read_text(encoding="utf-8")
        navigation = (ROOT / "_includes/navigation.html").read_text(encoding="utf-8")
        self.assertIn("if item.enabled != false", page)
        self.assertIn("if link.enabled != false", navigation)
        self.assertIn("case item.template", page)
        self.assertNotIn("<section", page)
        self.assertIn("site.data.news", template("news"))

    def test_data_driven_sections_have_bilingual_fields(self):
        profile = load_yaml("profile.yml")
        self.assertTrue(profile["paragraphs"])
        for item in profile["paragraphs"]:
            self.assertTrue(item["text_zh"])
            self.assertTrue(item["text_en"])
        for item in load_yaml("research.yml"):
            for field in ("title_zh", "title_en", "description_zh", "description_en"):
                self.assertTrue(item[field])
        teaching = load_yaml("teaching.yml")
        for semester in teaching["semesters"]:
            self.assertTrue(semester["name_zh"])
            self.assertTrue(semester["name_en"])
            for course in semester["courses"]:
                self.assertTrue(course["name_zh"])
                self.assertTrue(course["name_en"])
        contact = load_yaml("contact.yml")
        for field in ("address_zh", "address_en", "office_zh", "office_en"):
            self.assertTrue(contact[field])

    def test_teaching_courses_are_grouped_by_semester(self):
        teaching = load_yaml("teaching.yml")
        self.assertIsInstance(teaching["semesters"], list)
        for semester in teaching["semesters"]:
            self.assertIsInstance(semester["courses"], list)
        self.assertIn("site.data.teaching.semesters", template("teaching"))
        self.assertIn("semester.courses", template("teaching"))

    def test_yaml_collections_and_rendering_have_both_languages(self):
        fields = {"patents": "title", "projects": "title", "awards": "title"}
        for collection, field in fields.items():
            with self.subTest(collection=collection):
                records = load_yaml(f"{collection}.yml")
                self.assertTrue(records)
                for record in records:
                    self.assertTrue(record[f"{field}_zh"])
                    self.assertTrue(record[f"{field}_en"])
                block = template(collection)
                self.assertIn(f"site.data.{collection}", block)
                self.assertIn(f"{{{{ item.{field}_zh }}}}", block)
                self.assertIn(f"{{{{ item.{field}_en }}}}", block)
        projects = load_yaml("projects.yml")
        for project in projects:
            for field in ("role_zh", "role_en", "amount_zh", "amount_en"):
                self.assertTrue(project[field])
        projects_block = template("projects")
        for field in ("role_zh", "role_en", "amount_zh", "amount_en"):
            self.assertIn("{{ item." + field + " }}", projects_block)
        software = load_yaml("opensource.yml")
        self.assertTrue(software)
        self.assertTrue(all(item["name"] and item["url"] and item["description_zh"] and item["description_en"] for item in software))
        self.assertIn("site.data.opensource", template("opensource"))

    def test_student_data_and_template_are_bilingual(self):
        students = load_yaml("students.yml")
        self.assertTrue(students["competitions"])
        for item in students["competitions"]:
            self.assertTrue(item["title_zh"])
            self.assertTrue(item["title_en"])
        for grade in students["undergraduate"]:
            self.assertTrue(grade["grade_zh"])
            self.assertTrue(grade["grade_en"])
            for student in grade["profiles"]:
                for field in ("name_zh", "name_en", "status_zh", "status_en"):
                    self.assertTrue(student[field])
        block = template("students")
        self.assertIn("site.data.students.competitions", block)
        self.assertIn("site.data.students.undergraduate", block)

    def test_project_translations_are_nonempty_text(self):
        projects = load_yaml("projects.yml")
        for project in projects:
            for field in ("title_zh", "title_en"):
                self.assertIsInstance(project[field], str)
                self.assertTrue(project[field].strip())

    def test_navigation_order_and_project_metadata(self):
        # Ordering and visibility are editorial choices, not fixed snapshots.
        page = PAGE.read_text(encoding="utf-8")
        navigation = (ROOT / "_includes/navigation.html").read_text(encoding="utf-8")
        self.assertIn("for item in site.data.navigation.main", page)
        self.assertIn("for link in site.data.navigation.main", navigation)
        projects_block = template("projects")
        self.assertIn("· {{ item.amount_zh }} · {{ item.role_zh }}", projects_block)
        self.assertIn("· {{ item.amount_en }} · {{ item.role_en }}", projects_block)
        styles = (ROOT / "assets/css/site-overrides.css").read_text(encoding="utf-8")
        self.assertIn(".project h3 { display: inline;", styles)
        self.assertIn(".project p { display: inline;", styles)

    def test_patents_show_recent_records_first_with_author_emphasis(self):
        patents = load_yaml("patents.yml")
        dates = [item["display_date"] for item in patents]
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertTrue(all(item["status_zh"] != "已失效" for item in patents))
        block = template("patents")
        self.assertIn("<strong>{{ inventor }}</strong>", block)
        self.assertIn('class="publication-badges"', block)
        self.assertNotIn("patent-source", block)
        self.assertIn("limit: 5", block)
        self.assertIn('class="older-patents"', block)

    def test_main_journals_have_curated_metrics_in_generated_feed(self):
        records = json.loads((ROOT / "assets/data/site-data.json").read_text(encoding="utf-8"))["publications"]
        covered = {"Energy", "Energy Conversion and Management", "Renewable Energy", "Applied Energy", "Applied Thermal Engineering", "Journal of Energy Storage"}
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
