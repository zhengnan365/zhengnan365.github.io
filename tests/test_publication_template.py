import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "_includes/publication-item.html"
STYLESHEET = ROOT / "assets/css/pub.css"


class PublicationTemplateTests(unittest.TestCase):
    def test_row_uses_openalex_metadata_and_copy_control(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("{{ link.display_authors }}", template)
        self.assertIn("{{ link.venue | escape }}", template)
        self.assertIn("{{ link.year }}", template)
        self.assertIn("{{ link.doi | escape }}", template)
        self.assertIn("{{ link.citation_count }}", template)
        self.assertIn('<div class="title">{{ link.title | escape }}</div>', template)
        self.assertNotIn('<div class="title"><a ', template)
        self.assertIn('class="pub-badge doi-badge"', template)
        doi_badge = template.split('class="pub-badge doi-badge"', 1)[1].split('</a>', 1)[0]
        self.assertIn('fa-solid fa-link', doi_badge)
        self.assertIn('fa-quote-right', template)
        self.assertRegex(template, r"\{%\s*unless link\.citation_count == nil\s*%\}")
        self.assertRegex(
            template,
            r'<button[^>]+class="[^"]*citation-copy[^" ]*"[^>]+data-citation="\{\{ link\.citation_gbt7714 \| escape \}\}"',
        )
        self.assertNotRegex(template, r"(?i)<img\b|>PDF<|open.access|link\.pdf|link\.image")

    def test_each_metric_segment_is_guarded_independently(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn('class="publication-badges"', template)
        for field in ("impact_factor", "jcr_quartile"):
            self.assertIn(f"if link.metrics.{field}", template)
        self.assertIn("if link.metrics.cas_label_zh or link.metrics.cas_label_en", template)
        styles = STYLESHEET.read_text(encoding="utf-8")
        self.assertIn("--global-theme-color:", styles)
        self.assertIn('[data-theme="dark"] .publication-badges .pub-badge', styles)
        self.assertNotIn(".abbr", styles)
        self.assertNotIn(".teaser", styles)

    def test_dark_theme_year_and_external_link_have_contrast(self):
        styles = STYLESHEET.read_text(encoding="utf-8")
        self.assertRegex(styles, r'\[data-theme="dark"\] \.publications h3\.year[^{}]*\{[^}]*color:')
        self.assertRegex(styles, r'\[data-theme="dark"\] \.publication-badges \.pub-badge\s*\{[^}]*color:')
        self.assertIn('.publication-badges .doi-badge:hover', styles)
        self.assertIn('min-height: 25px;', styles)

    def test_publication_and_patent_titles_share_quiet_typography(self):
        styles = (ROOT / "assets/css/site-overrides.css").read_text(encoding="utf-8")
        self.assertRegex(
            styles,
            r"\.publication-card \.title,\s*\n\.patent-item \.title \{[^}]*font-size: 1em;[^}]*font-weight: 400;",
        )
        self.assertIn('.patent-item .author { margin: 3px 0; color: #555; font-size: .82em;', styles)
        self.assertIn('.patent-key-meta { margin: 3px 0 6px; color: #6b7076; font-size: .75em;', styles)
        self.assertIn('.patent-item .publication-badges .pub-badge {', styles)


if __name__ == "__main__":
    unittest.main()
