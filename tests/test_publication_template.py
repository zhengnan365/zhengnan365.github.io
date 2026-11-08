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
        self.assertIn("{{ link.openalex_url | escape }}", template)
        self.assertIn("{{ link.citation_count }}", template)
        self.assertRegex(template, r"\{%\s*unless link\.citation_count == nil\s*%\}")
        self.assertRegex(
            template,
            r'<button[^>]+class="[^"]*citation-copy[^" ]*"[^>]+data-citation="\{\{ link\.citation_gbt7714 \| escape \}\}"',
        )
        self.assertNotRegex(template, r"(?i)<img\b|>PDF<|open.access|link\.pdf|link\.image")

    def test_each_metric_segment_is_guarded_independently(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn('class="metrics-bar"', template)
        for field in ("impact_factor", "cas_label_zh", "cas_label_en", "jcr_quartile"):
            self.assertRegex(
                template,
                rf"\{{%\s*if link\.metrics\.{field}\s*%\}}(?:(?!\{{%\s*endif\s*%\}}).)*link\.metrics\.{field}",
            )
        styles = STYLESHEET.read_text(encoding="utf-8")
        self.assertIn("--global-theme-color:", styles)
        self.assertIn('[data-theme="dark"] .metrics-bar', styles)
        self.assertNotIn(".abbr", styles)
        self.assertNotIn(".teaser", styles)


if __name__ == "__main__":
    unittest.main()
