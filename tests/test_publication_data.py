import unittest

from scripts.publication_data import format_gbt7714, normalize_doi, normalize_work


AUTHOR_ID = "A5001145059"


def sample_work():
    return {
        "id": "https://openalex.org/W123",
        "doi": "https://doi.org/10.1234/Example.DOI",
        "title": "A representative energy paper",
        "publication_year": 2025,
        "publication_date": "2025-06-01",
        "type": "article",
        "cited_by_count": 12,
        "authorships": [
            {
                "author": {"id": "https://openalex.org/A111", "display_name": "First Author"},
                "raw_author_name": "First Author",
                "is_corresponding": True,
            },
            {
                "author": {"id": f"https://openalex.org/{AUTHOR_ID}", "display_name": "Nan Zheng"},
                "raw_author_name": "Nan Zheng",
                "is_corresponding": False,
            },
        ],
        "primary_location": {
            "source": {
                "display_name": "Applied Energy",
                "issn_l": "0306-2619",
                "issn": ["0306-2619", "1872-9118"],
            }
        },
        "biblio": {"volume": "350", "issue": "1", "first_page": "1", "last_page": "10"},
    }


class PublicationDataTests(unittest.TestCase):
    def test_normalize_doi_lowercases_and_removes_resolver(self):
        self.assertEqual(normalize_doi("https://doi.org/10.1234/Example.DOI"), "10.1234/example.doi")

    def test_normalize_work_marks_corresponding_author_and_bolds_owner(self):
        record = normalize_work(sample_work(), AUTHOR_ID, {}, {})
        self.assertIn("First Author*", record["display_authors"])
        self.assertIn("<strong>Nan Zheng</strong>", record["display_authors"])
        self.assertTrue(record["has_corresponding_author"])
        self.assertEqual(record["citation_count"], 12)
        self.assertEqual(record["citation_source"], "OpenAlex")

    def test_zero_citations_is_a_valid_count(self):
        work = sample_work()
        work["cited_by_count"] = 0
        record = normalize_work(work, AUTHOR_ID, {}, {})
        self.assertEqual(record["citation_count"], 0)

    def test_metrics_match_by_issn_l(self):
        metrics = {
            "0306-2619": {
                "journal": "Applied Energy",
                "metric_year": 2025,
                "impact_factor": 12.2,
                "cas_zone": 1,
                "cas_top": True,
                "jcr_quartile": "Q1",
            },
            "1872-9118": {"journal": "Wrong edition", "impact_factor": 99.9},
        }
        record = normalize_work(sample_work(), AUTHOR_ID, {}, metrics)
        self.assertEqual(record["metrics"]["impact_factor"], 12.2)
        self.assertEqual(record["metrics"]["cas_label_zh"], "中科院 1区 TOP")

    def test_metrics_fall_back_to_issn(self):
        work = sample_work()
        work["primary_location"]["source"]["issn_l"] = "0000-0000"
        metrics = {"1872-9118": {"journal": "Applied Energy", "impact_factor": 12.2}}
        record = normalize_work(work, AUTHOR_ID, {}, metrics)
        self.assertEqual(record["metrics"]["impact_factor"], 12.2)

    def test_unmatched_journal_has_no_metrics(self):
        work = sample_work()
        work["primary_location"]["source"]["issn_l"] = "0000-0000"
        work["primary_location"]["source"]["issn"] = ["1111-1111"]
        metrics = {"0306-2619": {"journal": "Applied Energy", "impact_factor": 12.2}}
        record = normalize_work(work, AUTHOR_ID, {}, metrics)
        self.assertIsNone(record["metrics"])

    def test_formats_complete_gbt7714_journal_citation(self):
        record = normalize_work(sample_work(), AUTHOR_ID, {}, {})
        self.assertEqual(
            record["citation_gbt7714"],
            "First Author, Nan Zheng. A representative energy paper[J]. Applied Energy, 2025, 350(1): 1-10. DOI: 10.1234/example.doi.",
        )

    def test_formats_partial_citation_without_empty_punctuation(self):
        work = sample_work()
        work["doi"] = None
        work["biblio"] = {}
        record = normalize_work(work, AUTHOR_ID, {}, {})
        self.assertEqual(
            record["citation_gbt7714"],
            "First Author, Nan Zheng. A representative energy paper[J]. Applied Energy, 2025.",
        )

    def test_formats_citation_without_authors_or_optional_metadata(self):
        self.assertEqual(
            format_gbt7714({"title": "Standalone title", "type": "article"}),
            "Standalone title[J].",
        )

    def test_omits_issue_when_volume_is_missing(self):
        work = sample_work()
        work["biblio"] = {"issue": "2"}
        record = normalize_work(work, AUTHOR_ID, {}, {})
        self.assertEqual(
            record["citation_gbt7714"],
            "First Author, Nan Zheng. A representative energy paper[J]. Applied Energy, 2025. DOI: 10.1234/example.doi.",
        )

    def test_omits_missing_venue_year_and_pages(self):
        work = sample_work()
        work["primary_location"]["source"]["display_name"] = None
        work["publication_year"] = None
        work["biblio"] = {}
        record = normalize_work(work, AUTHOR_ID, {}, {})
        self.assertEqual(
            record["citation_gbt7714"],
            "First Author, Nan Zheng. A representative energy paper[J]. DOI: 10.1234/example.doi.",
        )

    def test_preserves_legitimate_double_periods(self):
        self.assertEqual(
            format_gbt7714(
                {
                    "authors": "A Author",
                    "title": "A..B",
                    "type": "article",
                    "venue": "Journal",
                    "year": 2025,
                    "doi": "10.1234/foo..bar",
                }
            ),
            "A Author. A..B[J]. Journal, 2025. DOI: 10.1234/foo..bar.",
        )


if __name__ == "__main__":
    unittest.main()
