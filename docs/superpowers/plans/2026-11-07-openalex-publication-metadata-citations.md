# OpenAlex Publication Metadata and Citations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the single-page Jekyll academic website so OpenAlex automatically supplies publication metadata, corresponding-author marks, attributed citation counts, and GB/T 7714—2015 citations while curated journal metrics and bilingual theme controls remain stable.

**Architecture:** Keep `scripts/sync_publications.py` as the network and file orchestration entry point, but move normalization, GB/T formatting, override application, and journal-metric matching into a testable `scripts/publication_data.py` module. Jekyll renders the generated YAML through a compact publication component; an ES module owns language, theme, and clipboard behavior; the separate personal website consumes the same generated JSON feed.

**Tech Stack:** Jekyll 3.8/Minimal Light, Liquid, SCSS/CSS, vanilla JavaScript ES modules, Python 3.12+ standard library, PyYAML, Python `unittest`, Node.js built-in test runner, GitHub Actions, OpenAlex REST API.

---

## File responsibility map

- `scripts/publication_data.py`: pure publication normalization, author markup, metric matching, and GB/T citation formatting.
- `scripts/sync_publications.py`: OpenAlex HTTP requests, override/metric loading, validation, atomic YAML/JSON output.
- `tests/test_publication_data.py`: Python unit tests for publication-domain behavior.
- `tests/test_sync_publications.py`: synchronization and output-preservation tests.
- `tests/site-controls.test.mjs`: JavaScript unit tests for language, theme, and clipboard behavior.
- `_data/journal_metrics.yml`: manually verified journal metrics with edition and source provenance.
- `_data/overrides.yml`: exceptional corrections or exclusions keyed by DOI/OpenAlex ID.
- `_data/publications.yml`: generated Jekyll publication data.
- `assets/data/site-data.json`: generated shared data feed.
- `_includes/publication-item.html`: one publication row.
- `_includes/publications.md`: year grouping and section heading.
- `_includes/topnav.html`, `_includes/navigation.html`, `_data/navigation.yml`: fixed navigation and controls.
- `assets/js/site-controls.mjs`: browser language/theme/copy controller.
- `assets/css/pub.css`, `assets/css/nav.css`, `assets/css/style.scss`: publication, navigation, theme, avatar, and responsive styling.
- `index.md`: bilingual page content.
- `.github/workflows/sync-publications.yml`: weekly tests and OpenAlex refresh.
- `D:\00Keyan\18-课题组\个人网站\index.html`: remote JSON consumer and matching publication controls.
- `D:\00Keyan\18-课题组\个人网站\data\site-data.json`: local fallback feed.

### Task 1: Extract and test publication normalization

**Files:**
- Create: `scripts/publication_data.py`
- Create: `tests/test_publication_data.py`
- Modify: `scripts/sync_publications.py`

- [ ] **Step 1: Write failing tests for DOI normalization, corresponding authors, and citation metadata**

Create `tests/test_publication_data.py` with a representative OpenAlex work. The test fixture must identify Nan Zheng by OpenAlex ID rather than name alone and must include one separate corresponding author.

```python
import unittest

from scripts.publication_data import normalize_doi, normalize_work


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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify they fail before the module exists**

Run:

```powershell
python -m unittest tests.test_publication_data -v
```

Expected: `ModuleNotFoundError: No module named 'scripts.publication_data'`.

- [ ] **Step 3: Implement the pure normalization module**

Create `scripts/publication_data.py` with these public functions and field names:

```python
from __future__ import annotations

import html
import re
from typing import Any


def short_openalex_id(value: str | None) -> str:
    return (value or "").rstrip("/").rsplit("/", 1)[-1]


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    return doi.lower() or None


def doi_url(value: str | None) -> str | None:
    doi = normalize_doi(value)
    return f"https://doi.org/{doi}" if doi else None


def build_author_fields(authorships: list[dict[str, Any]], owner_author_id: str) -> tuple[str, str, bool]:
    plain_names: list[str] = []
    display_names: list[str] = []
    has_corresponding = False
    for authorship in authorships:
        author = authorship.get("author") or {}
        name = author.get("display_name") or authorship.get("raw_author_name") or "Unknown author"
        is_corresponding = bool(authorship.get("is_corresponding"))
        has_corresponding = has_corresponding or is_corresponding
        suffix = "*" if is_corresponding else ""
        escaped = html.escape(name)
        if short_openalex_id(author.get("id")) == owner_author_id:
            escaped = f"<strong>{escaped}</strong>"
        plain_names.append(f"{name}{suffix}")
        display_names.append(f"{escaped}{suffix}")
    return ", ".join(plain_names), ", ".join(display_names), has_corresponding


def normalize_work(
    work: dict[str, Any],
    owner_author_id: str,
    overrides: dict[str, dict[str, Any]],
    metrics: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source = (work.get("primary_location") or {}).get("source") or {}
    authors, display_authors, has_corresponding = build_author_fields(
        work.get("authorships") or [], owner_author_id
    )
    normalized_doi = normalize_doi(work.get("doi"))
    stable_id = normalized_doi or short_openalex_id(work.get("id"))
    biblio = work.get("biblio") or {}
    record = {
        "id": work.get("id"),
        "stable_id": stable_id,
        "doi": doi_url(normalized_doi),
        "title": work.get("title") or "Untitled work",
        "authors": authors,
        "display_authors": display_authors,
        "has_corresponding_author": has_corresponding,
        "venue": source.get("display_name") or "",
        "issn_l": source.get("issn_l"),
        "issns": source.get("issn") or [],
        "year": work.get("publication_year"),
        "date": work.get("publication_date"),
        "type": work.get("type"),
        "volume": biblio.get("volume"),
        "issue": biblio.get("issue"),
        "first_page": biblio.get("first_page"),
        "last_page": biblio.get("last_page"),
        "url": doi_url(normalized_doi) or work.get("id"),
        "openalex_url": work.get("id"),
        "citation_count": work.get("cited_by_count"),
        "citation_source": "OpenAlex",
    }
    override = overrides.get(normalized_doi or "") or overrides.get(work.get("id") or "") or {}
    record["_exclude"] = bool(override.get("exclude"))
    record.update({key: value for key, value in override.items() if key != "exclude"})
    return record
```

Temporarily leave metric matching and GB/T generation for Tasks 2 and 3; the function must still accept both dictionaries so later signatures do not change.

- [ ] **Step 4: Run the focused tests**

Run:

```powershell
python -m unittest tests.test_publication_data -v
```

Expected: 3 tests pass.

- [ ] **Step 5: Commit the normalization boundary**

```powershell
git add scripts/publication_data.py tests/test_publication_data.py
git commit -m "test: define publication normalization"
```

### Task 2: Add journal metric matching and provenance

**Files:**
- Create: `_data/journal_metrics.yml`
- Modify: `scripts/publication_data.py`
- Modify: `tests/test_publication_data.py`

- [ ] **Step 1: Add failing metric-matching tests**

Append tests that prefer ISSN-L and omit unmatched metrics:

```python
    def test_metrics_match_by_issn_l(self):
        metrics = {
            "0306-2619": {
                "journal": "Applied Energy",
                "metric_year": 2025,
                "impact_factor": 11.2,
                "cas_zone": 1,
                "cas_top": True,
                "jcr_quartile": "Q1",
            }
        }
        record = normalize_work(sample_work(), AUTHOR_ID, {}, metrics)
        self.assertEqual(record["metrics"]["impact_factor"], 11.2)
        self.assertEqual(record["metrics"]["cas_label_zh"], "中科院 1区 TOP")

    def test_unmatched_journal_has_no_metrics(self):
        work = sample_work()
        work["primary_location"]["source"]["issn_l"] = "0000-0000"
        record = normalize_work(work, AUTHOR_ID, {}, {})
        self.assertIsNone(record["metrics"])
```

- [ ] **Step 2: Run the tests and verify the new assertions fail**

Run:

```powershell
python -m unittest tests.test_publication_data.PublicationDataTests.test_metrics_match_by_issn_l tests.test_publication_data.PublicationDataTests.test_unmatched_journal_has_no_metrics -v
```

Expected: failures because `metrics` is not yet included in normalized records.

- [ ] **Step 3: Implement exact metric matching**

Add to `scripts/publication_data.py`:

```python
def match_metrics(source: dict[str, Any], metrics: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    keys = [source.get("issn_l"), *(source.get("issn") or [])]
    item = next((metrics[key] for key in keys if key and key in metrics), None)
    if not item:
        return None
    result = dict(item)
    zone = result.get("cas_zone")
    if zone:
        result["cas_label_zh"] = f"中科院 {zone}区" + (" TOP" if result.get("cas_top") else "")
        result["cas_label_en"] = f"CAS Zone {zone}" + (" TOP" if result.get("cas_top") else "")
    return result
```

In `normalize_work`, set:

```python
        "metrics": match_metrics(source, metrics),
```

- [ ] **Step 4: Create the production metric data schema and curate verified entries**

Create `_data/journal_metrics.yml` keyed by ISSN-L. Every displayed value must carry its edition and source URL. Use this exact schema:

```yaml
"0306-2619":
  journal: Applied Energy
  metric_year: 2025
  impact_factor: 11.2
  cas_edition: 2025
  cas_zone: 1
  cas_top: true
  jcr_quartile: Q1
  source_url: "https://www.sciencedirect.com/journal/applied-energy/about/insights"
```

Before adding another journal, verify the current official journal metric and the same CAS/JCR edition. Do not add a record when the impact factor, CAS partition, TOP status, or JCR quartile cannot be verified; unmatched journals intentionally render no bar.

- [ ] **Step 5: Run metric tests and YAML validation**

Run:

```powershell
python -m unittest tests.test_publication_data -v
python -c "import yaml; d=yaml.safe_load(open('_data/journal_metrics.yml', encoding='utf-8')); assert all(v.get('metric_year') and v.get('source_url') for v in d.values()); print(len(d), 'verified journal metric records')"
```

Expected: all unit tests pass and the command prints a positive verified record count.

- [ ] **Step 6: Commit metric support**

```powershell
git add scripts/publication_data.py tests/test_publication_data.py _data/journal_metrics.yml
git commit -m "feat: add curated journal metrics"
```

### Task 3: Generate GB/T 7714—2015 citations

**Files:**
- Modify: `scripts/publication_data.py`
- Modify: `tests/test_publication_data.py`

- [ ] **Step 1: Add failing tests for complete and partial journal citations**

```python
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
```

- [ ] **Step 2: Verify both tests fail**

Run:

```powershell
python -m unittest tests.test_publication_data.PublicationDataTests.test_formats_complete_gbt7714_journal_citation tests.test_publication_data.PublicationDataTests.test_formats_partial_citation_without_empty_punctuation -v
```

Expected: failures because `citation_gbt7714` is missing.

- [ ] **Step 3: Implement deterministic citation formatting**

Add these functions to `scripts/publication_data.py`:

```python
def page_range(first_page: str | None, last_page: str | None) -> str | None:
    if first_page and last_page and first_page != last_page:
        return f"{first_page}-{last_page}"
    return first_page or last_page


def format_gbt7714(record: dict[str, Any]) -> str:
    type_mark = "J" if record.get("type") in {"article", "review"} else "C"
    parts = [f"{record['authors'].replace('*', '')}. {record['title']}[{type_mark}]."]
    publication = record.get("venue") or ""
    if record.get("year"):
        publication += f", {record['year']}"
    volume_issue = record.get("volume") or ""
    if record.get("issue"):
        volume_issue += f"({record['issue']})"
    if volume_issue:
        publication += f", {volume_issue}"
    pages = page_range(record.get("first_page"), record.get("last_page"))
    if pages:
        publication += f": {pages}"
    if publication:
        parts.append(f" {publication}.")
    normalized_doi = normalize_doi(record.get("doi"))
    if normalized_doi:
        parts.append(f" DOI: {normalized_doi}.")
    return "".join(parts).replace("..", ".")
```

At the end of `normalize_work`, after overrides are applied, set:

```python
    record["citation_gbt7714"] = record.get("citation_gbt7714") or format_gbt7714(record)
```

- [ ] **Step 4: Run all publication-domain tests**

Run:

```powershell
python -m unittest tests.test_publication_data -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit citation formatting**

```powershell
git add scripts/publication_data.py tests/test_publication_data.py
git commit -m "feat: generate GB/T publication citations"
```

### Task 4: Make OpenAlex synchronization complete and failure-safe

**Files:**
- Modify: `scripts/sync_publications.py`
- Create: `tests/test_sync_publications.py`
- Modify: `_data/overrides.yml`

- [ ] **Step 1: Add failing synchronization tests**

Create `tests/test_sync_publications.py`:

```python
import json
import tempfile
import unittest
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
            yaml_records = yaml.safe_load((root / "_data/publications.yml").read_text(encoding="utf-8"))["main"]
            json_records = json.loads((root / "assets/data/site-data.json").read_text(encoding="utf-8"))["publications"]
            self.assertEqual(yaml_records, json_records)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify missing interfaces fail**

Run:

```powershell
python -m unittest tests.test_sync_publications -v
```

Expected: failures because `build_records` and the injectable `write_outputs(records, root)` interface do not exist.

- [ ] **Step 3: Rewrite the synchronizer around pure records and atomic output**

Update the OpenAlex `select` list to exactly include:

```python
SELECT_FIELDS = ",".join(
    [
        "id", "doi", "title", "publication_year", "publication_date", "type",
        "authorships", "corresponding_author_ids", "primary_location", "biblio",
        "cited_by_count",
    ]
)
```

Load metrics and overrides with YAML mappings, then normalize through `publication_data.normalize_work`. Define these interfaces:

```python
def build_records(works: list[dict], overrides: dict, metrics: dict) -> list[dict]:
    if not works:
        raise RuntimeError("OpenAlex returned no works; preserving previous generated data")
    unique: dict[str, dict] = {}
    for work in works:
        record = normalize_work(work, AUTHOR_ID, overrides, metrics)
        if record.pop("_exclude", False):
            continue
        key = record.get("stable_id")
        if key:
            unique[key] = record
    if not unique:
        raise RuntimeError("No valid publications remained after normalization")
    return sorted(unique.values(), key=lambda item: (item.get("year") or 0, item.get("date") or ""), reverse=True)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)
```

`write_outputs(records, root=ROOT)` must serialize the identical `records` list to YAML and JSON, preserve `generated_at` when records are unchanged, validate the just-built strings before replacing files, and only then call `atomic_write`.

- [ ] **Step 4: Document the override schema**

Replace the current example in `_data/overrides.yml` with valid examples that remain commented:

```yaml
# Overrides are keyed by normalized DOI or full OpenAlex work ID.
# "10.1000/example":
#   exclude: true
# "https://openalex.org/W1234567890":
#   display_authors: "Author A, <strong>Nan Zheng</strong>*"
#   has_corresponding_author: true
```

- [ ] **Step 5: Run all Python tests and regenerate data**

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/sync_publications.py
python -c "import json,yaml; y=yaml.safe_load(open('_data/publications.yml',encoding='utf-8'))['main']; j=json.load(open('assets/data/site-data.json',encoding='utf-8'))['publications']; assert y==j; assert len(y)>0; assert len({x['stable_id'] for x in y})==len(y); print(len(y),'publications validated')"
```

Expected: tests pass, synchronization reports a non-zero publication count, and YAML/JSON records match exactly.

- [ ] **Step 6: Commit safe synchronization**

```powershell
git add scripts/sync_publications.py scripts/publication_data.py tests/test_sync_publications.py _data/overrides.yml _data/publications.yml assets/data/site-data.json
git commit -m "feat: synchronize complete OpenAlex metadata safely"
```

### Task 5: Render the compact publication row

**Files:**
- Modify: `_includes/publication-item.html`
- Modify: `_includes/publications.md`
- Modify: `assets/css/pub.css`
- Modify: `assets/css/style.scss`

- [ ] **Step 1: Add a static template-contract check**

Create `tests/test_publication_template.py`:

```python
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicationTemplateTests(unittest.TestCase):
    def test_publication_item_has_required_controls_only(self):
        template = (ROOT / "_includes/publication-item.html").read_text(encoding="utf-8")
        self.assertIn("citation_count", template)
        self.assertIn("citation_gbt7714", template)
        self.assertIn("metrics-bar", template)
        self.assertNotIn(">PDF<", template)
        self.assertNotIn("Open Access", template)
        self.assertNotIn("<img", template)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the check and verify the current template fails**

Run:

```powershell
python -m unittest tests.test_publication_template -v
```

Expected: failures for missing citation/metric fields and the existing image/PDF/Open Access markup.

- [ ] **Step 3: Replace the publication item markup**

Use this structure in `_includes/publication-item.html`:

```liquid
{% assign link = include.link %}
<li class="publication-item">
  <article class="publication-card">
    <div class="title"><a href="{{ link.url }}" target="_blank" rel="noopener">{{ link.title }}</a></div>
    <div class="author">{{ link.display_authors }}</div>
    {% if link.metrics %}
    <div class="metrics-bar" aria-label="Journal metrics">
      <span><span class="i18n-zh">影响因子</span><span class="i18n-en">Impact Factor</span> {{ link.metrics.impact_factor }}</span>
      <span><span class="i18n-zh">{{ link.metrics.cas_label_zh }}</span><span class="i18n-en">{{ link.metrics.cas_label_en }}</span></span>
      <span>JCR {{ link.metrics.jcr_quartile }}</span>
    </div>
    {% endif %}
    <div class="periodical"><em>{{ link.venue }}{% if link.year %}, {{ link.year }}{% endif %}.</em></div>
    <div class="links">
      {% if link.doi %}<a href="{{ link.doi }}" class="btn" target="_blank" rel="noopener">DOI</a>{% endif %}
      {% unless link.citation_count == nil %}<a href="{{ link.openalex_url }}" class="btn" target="_blank" rel="noopener"><span class="i18n-zh">OpenAlex 引用 {{ link.citation_count }}</span><span class="i18n-en">{{ link.citation_count }} OpenAlex citations</span></a>{% endunless %}
      <button type="button" class="btn citation-copy" data-citation="{{ link.citation_gbt7714 | escape }}"><span class="i18n-zh">引用</span><span class="i18n-en">Cite</span></button>
    </div>
  </article>
</li>
```

- [ ] **Step 4: Replace thumbnail-era CSS with compact rows and segmented metrics**

Remove `.abbr`, `.teaser`, and image-column rules. Add compact rules with the approved segmented bar:

```css
.publications ol.bibliography li.publication-item { min-height: 0; padding: 12px 16px; }
.publication-card .author { color: #555; font-size: .95em; margin: 3px 0; }
.metrics-bar { display: inline-flex; flex-wrap: wrap; overflow: hidden; margin: 5px 0; border: 1px solid #d6dee8; border-radius: 5px; font-size: 11.5px; }
.metrics-bar > span { padding: 2px 8px; background: #f5f7fa; color: #31445b; }
.metrics-bar > span + span { border-left: 1px solid #d6dee8; }
.publication-card .links { display: flex; flex-wrap: wrap; gap: 5px; }
.publication-card .btn { appearance: none; background: transparent; color: #444; border: 1px solid #bbb; border-radius: 4px; padding: 2px 8px; font: inherit; font-size: 11.5px; cursor: pointer; }
.publication-card .btn:hover { color: #fff; background: var(--global-theme-color); border-color: var(--global-theme-color); }
[data-theme="dark"] .publication-card .author { color: #c7d0dc; }
[data-theme="dark"] .metrics-bar { border-color: #50647a; }
[data-theme="dark"] .metrics-bar > span { color: #e9eef5; background: #25364a; }
[data-theme="dark"] .metrics-bar > span + span { border-left-color: #50647a; }
```

- [ ] **Step 5: Run the template check**

Run:

```powershell
python -m unittest tests.test_publication_template -v
```

Expected: pass.

- [ ] **Step 6: Commit the publication component**

```powershell
git add _includes/publication-item.html _includes/publications.md assets/css/pub.css assets/css/style.scss tests/test_publication_template.py
git commit -m "feat: render publication metrics and citation controls"
```

### Task 6: Add tested language, theme, and clipboard controls

**Files:**
- Create: `assets/js/site-controls.mjs`
- Create: `tests/site-controls.test.mjs`
- Modify: `_layouts/homepage.html`
- Modify: `_includes/topnav.html`
- Modify: `_includes/navigation.html`
- Modify: `_data/navigation.yml`
- Modify: `assets/css/nav.css`
- Modify: `assets/css/style.scss`

- [ ] **Step 1: Write failing Node tests for labels and clipboard behavior**

Create `tests/site-controls.test.mjs`:

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { copyCitation, nextLanguage, nextTheme } from '../assets/js/site-controls.mjs';

test('language toggles between Chinese and English', () => {
  assert.equal(nextLanguage('zh'), 'en');
  assert.equal(nextLanguage('en'), 'zh');
});

test('theme toggles between light and dark', () => {
  assert.equal(nextTheme('light'), 'dark');
  assert.equal(nextTheme('dark'), 'light');
});

test('copyCitation uses the Clipboard API when available', async () => {
  let copied = '';
  await copyCitation('citation text', { writeText: async value => { copied = value; } });
  assert.equal(copied, 'citation text');
});
```

- [ ] **Step 2: Run the Node tests and verify the module is missing**

Run:

```powershell
node --test tests/site-controls.test.mjs
```

Expected: `ERR_MODULE_NOT_FOUND`.

- [ ] **Step 3: Implement the browser module with testable pure functions**

Create `assets/js/site-controls.mjs`:

```javascript
export const nextLanguage = language => language === 'en' ? 'zh' : 'en';
export const nextTheme = theme => theme === 'dark' ? 'light' : 'dark';

export async function copyCitation(text, clipboard = navigator.clipboard) {
  if (clipboard?.writeText) return clipboard.writeText(text);
  const area = document.createElement('textarea');
  area.value = text;
  area.setAttribute('readonly', '');
  area.style.position = 'fixed';
  area.style.opacity = '0';
  document.body.appendChild(area);
  area.select();
  const copied = document.execCommand('copy');
  area.remove();
  if (!copied) throw new Error('Copy command failed');
}

function updateControlLabels(doc) {
  const language = doc.documentElement.dataset.lang || 'zh';
  doc.querySelector('[data-language-toggle]')?.replaceChildren(language === 'zh' ? 'EN' : '中');
  doc.querySelector('[data-theme-toggle]')?.replaceChildren(doc.documentElement.dataset.theme === 'dark' ? '☀' : '☾');
}

export function initializeSiteControls(doc = document, storage = localStorage) {
  const root = doc.documentElement;
  root.dataset.lang = storage.getItem('site-language') || 'zh';
  root.dataset.theme = storage.getItem('site-theme') || 'light';
  updateControlLabels(doc);

  doc.querySelector('[data-language-toggle]')?.addEventListener('click', () => {
    root.dataset.lang = nextLanguage(root.dataset.lang);
    storage.setItem('site-language', root.dataset.lang);
    updateControlLabels(doc);
  });
  doc.querySelector('[data-theme-toggle]')?.addEventListener('click', () => {
    root.dataset.theme = nextTheme(root.dataset.theme);
    storage.setItem('site-theme', root.dataset.theme);
    updateControlLabels(doc);
  });
  doc.querySelectorAll('.citation-copy').forEach(button => button.addEventListener('click', async () => {
    const language = root.dataset.lang || 'zh';
    try {
      await copyCitation(button.dataset.citation || '');
      button.textContent = language === 'zh' ? '已复制' : 'Copied';
    } catch {
      button.textContent = language === 'zh' ? '复制失败' : 'Copy failed';
    }
    window.setTimeout(() => {
      button.innerHTML = '<span class="i18n-zh">引用</span><span class="i18n-en">Cite</span>';
    }, 1600);
  }));
}

if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => initializeSiteControls());
}
```

- [ ] **Step 4: Add navigation controls and bilingual navigation data**

Use `title_zh` and `title_en` in `_data/navigation.yml`, render both spans in `_includes/navigation.html`, and add these buttons before the mobile menu icon in `_includes/topnav.html`:

```html
<div class="topnav-controls" aria-label="Display controls">
  <button type="button" data-language-toggle aria-label="切换语言">EN</button>
  <button type="button" data-theme-toggle aria-label="切换明暗模式">☾</button>
</div>
```

Load the module near the end of `_layouts/homepage.html`:

```html
<script type="module" src="{{ '/assets/js/site-controls.mjs' | relative_url }}"></script>
```

Also initialize the root element before JavaScript runs:

```html
<html lang="zh-CN" data-lang="zh" data-theme="light">
```

- [ ] **Step 5: Add theme, language, control, and avatar-shadow styles**

Add to `assets/css/style.scss`:

```scss
html[data-lang="zh"] .i18n-en, html[data-lang="en"] .i18n-zh { display: none !important; }
html[data-theme="dark"] { color-scheme: dark; }
html[data-theme="dark"] body { background: #111923; color: #e7edf4; }
html[data-theme="dark"] a { color: #8bbbe8; }
html[data-theme="dark"] section > h2 { border-bottom-color: rgba(255,255,255,.16); }
.avatar img { box-shadow: 0 9px 24px rgba(9, 27, 48, .25); }
```

Add `.topnav-controls` styles to `assets/css/nav.css`, keeping both controls visible on desktop and inside the 960-pixel layout without colliding with the hamburger button.

- [ ] **Step 6: Run JavaScript and Python tests**

Run:

```powershell
node --test tests/site-controls.test.mjs
python -m unittest discover -s tests -p "test_*.py" -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit the controls**

```powershell
git add assets/js/site-controls.mjs tests/site-controls.test.mjs _layouts/homepage.html _includes/topnav.html _includes/navigation.html _data/navigation.yml assets/css/nav.css assets/css/style.scss
git commit -m "feat: add bilingual theme and citation controls"
```

### Task 7: Make the full page bilingual

**Files:**
- Modify: `index.md`
- Modify: `_includes/publications.md`
- Modify: `_data/patents.yml`
- Modify: `_data/projects.yml`
- Modify: `_data/awards.yml`
- Modify: `_data/news.yml`

- [ ] **Step 1: Add a static bilingual-content test**

Create `tests/test_bilingual_content.py`:

```python
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BilingualContentTests(unittest.TestCase):
    def test_requested_sections_have_both_language_markers(self):
        page = (ROOT / "index.md").read_text(encoding="utf-8")
        for section_id in ["about", "research", "patents", "projects", "students", "awards", "news"]:
            start = page.index(f'id="{section_id}"')
            next_section = page.find('<section', start + 1)
            block = page[start: next_section if next_section != -1 else len(page)]
            self.assertIn("i18n-zh", block, section_id)
            self.assertIn("i18n-en", block, section_id)
        publications = (ROOT / "_includes/publications.md").read_text(encoding="utf-8")
        self.assertIn("i18n-zh", publications)
        self.assertIn("i18n-en", publications)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify current Chinese-only sections fail**

Run:

```powershell
python -m unittest tests.test_bilingual_content -v
```

Expected: failure beginning with the `about` or `research` section.

- [ ] **Step 3: Add parallel Chinese and English interface content**

For headings and paragraphs in `index.md`, use paired spans or blocks:

```html
<h2><span class="i18n-zh">个人经历</span><span class="i18n-en">About Me</span></h2>
<div class="i18n-zh"><p>郑楠，工学博士，讲师，硕士生导师，现任职于扬州大学电气与能源动力工程学院。2024 年毕业于华北电力大学动力工程及工程热物理专业（硕博连读），曾于比萨大学联合培养。</p></div>
<div class="i18n-en"><p>Nan Zheng is a lecturer and master's supervisor at the College of Electrical, Energy and Power Engineering, Yangzhou University. He received his Ph.D. in Power Engineering and Engineering Thermophysics from North China Electric Power University in 2024 and completed joint doctoral training at the University of Pisa.</p></div>
```

Apply the same pattern to research descriptions, project roles, student recruitment text, award descriptions, news, contact labels, publication section title/note, and action labels. Keep publication title, author names, and venue names as a single untranslated value.

Where a data collection is rendered from YAML, add `title_zh`/`title_en`, `role_zh`/`role_en`, or `text_zh`/`text_en` fields and render them in paired spans.

- [ ] **Step 4: Run bilingual and full test suites**

Run:

```powershell
python -m unittest tests.test_bilingual_content -v
python -m unittest discover -s tests -p "test_*.py" -v
node --test tests/site-controls.test.mjs
```

Expected: all tests pass.

- [ ] **Step 5: Commit bilingual page content**

```powershell
git add index.md _includes/publications.md _data/patents.yml _data/projects.yml _data/awards.yml _data/news.yml tests/test_bilingual_content.py
git commit -m "feat: provide Chinese and English page content"
```

### Task 8: Update automation and the separate personal website

**Files:**
- Modify: `.github/workflows/sync-publications.yml`
- Modify: `D:\00Keyan\18-课题组\个人网站\index.html`
- Create or update: `D:\00Keyan\18-课题组\个人网站\data\site-data.json`

- [ ] **Step 1: Make the sync workflow weekly and test-first**

Change the schedule to Monday at 02:20 UTC and run tests before synchronization:

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: "20 2 * * 1"

steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: "3.12"
  - run: python -m pip install --disable-pip-version-check pyyaml
  - run: python -m unittest discover -s tests -p "test_*.py" -v
  - run: python scripts/sync_publications.py
```

Keep the existing conditional commit, but include `_data/journal_metrics.yml` only as an input, never as generated output.

- [ ] **Step 2: Replace the separate website's old PDF/Open Access renderer**

Update `renderPublications` in `D:\00Keyan\18-课题组\个人网站\index.html` so each row renders:

```javascript
const metrics = item.metrics ? `<div class="metrics-bar"><span>${language === 'zh' ? '影响因子' : 'Impact Factor'} ${escapeHtml(item.metrics.impact_factor)}</span><span>${escapeHtml(language === 'zh' ? item.metrics.cas_label_zh : item.metrics.cas_label_en)}</span><span>JCR ${escapeHtml(item.metrics.jcr_quartile)}</span></div>` : '';
const citationCount = item.citation_count === null || item.citation_count === undefined ? '' : `<a href="${escapeHtml(item.openalex_url)}" target="_blank" rel="noopener">${language === 'zh' ? `OpenAlex 引用 ${item.citation_count}` : `${item.citation_count} OpenAlex citations`}</a>`;
return `<li class="pub-item"><div><div class="pub-title"><a href="${escapeHtml(item.url)}" target="_blank" rel="noopener">${escapeHtml(item.title)}</a></div><div class="pub-meta">${item.display_authors || escapeHtml(item.authors)}</div>${metrics}<div class="pub-meta"><em>${escapeHtml(item.venue)}, ${escapeHtml(item.year)}</em></div><div class="pub-links">${item.doi ? `<a href="${escapeHtml(item.doi)}" target="_blank">DOI</a>` : ''}${citationCount}<button class="citation-copy" data-citation="${escapeHtml(item.citation_gbt7714)}">${language === 'zh' ? '引用' : 'Cite'}</button></div></div></li>`;
```

Render all year groups rather than the earlier “latest eight + older” collapse so it matches the canonical GitHub Pages site.

- [ ] **Step 3: Update the local fallback feed**

Run:

```powershell
New-Item -ItemType Directory -Force 'D:\00Keyan\18-课题组\个人网站\data' | Out-Null
Copy-Item -LiteralPath 'D:\00Keyan\WorkSpace\zhengnan365.github.io\assets\data\site-data.json' -Destination 'D:\00Keyan\18-课题组\个人网站\data\site-data.json' -Force
```

Expected: the fallback JSON contains the same `generated_at` and publication records as the canonical feed.

- [ ] **Step 4: Validate workflow YAML and shared JSON**

Run:

```powershell
python -c "import yaml; yaml.safe_load(open('.github/workflows/sync-publications.yml',encoding='utf-8')); print('workflow yaml valid')"
python -c "import json; a=json.load(open('assets/data/site-data.json',encoding='utf-8')); b=json.load(open(r'D:\00Keyan\18-课题组\个人网站\data\site-data.json',encoding='utf-8')); assert a==b; print('shared feed matches fallback')"
```

Expected: both validation messages print.

- [ ] **Step 5: Commit canonical-repository automation changes**

```powershell
git add .github/workflows/sync-publications.yml
git commit -m "ci: test and refresh publications weekly"
```

Do not commit files from `D:\00Keyan\18-课题组\个人网站` unless that folder is independently confirmed to be a Git repository; preserve its existing unrelated files.

### Task 9: End-to-end verification

**Files:**
- Verify: all changed files in both website roots

- [ ] **Step 1: Run all automated tests and static validation**

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
node --test tests/site-controls.test.mjs
python -c "import json,yaml; yaml.safe_load(open('_data/publications.yml',encoding='utf-8')); yaml.safe_load(open('_data/journal_metrics.yml',encoding='utf-8')); json.load(open('assets/data/site-data.json',encoding='utf-8')); print('generated data valid')"
git diff --check
```

Expected: all tests pass, data parses, and `git diff --check` reports no errors.

- [ ] **Step 2: Verify generated publication invariants**

Run:

```powershell
python -c "import yaml; p=yaml.safe_load(open('_data/publications.yml',encoding='utf-8'))['main']; assert p; assert all(x.get('year') for x in p); assert all('citation_gbt7714' in x for x in p); assert all('citation_source' in x for x in p); assert len({x['stable_id'] for x in p})==len(p); print(len(p),'publication records verified')"
```

Expected: non-zero verified records with no duplicate stable IDs.

- [ ] **Step 3: Inspect desktop and mobile browser behavior**

Use the existing static preview approach and inspect at desktop width and 390 pixels. Verify:

- fixed navy navigation stays visible;
- language defaults to Chinese and switches all interface content;
- theme defaults to light and switches without reload;
- avatar has a soft shadow;
- publication thumbnails, PDF, and Open Access controls are absent;
- `姓名*` appears for OpenAlex-identified corresponding authors;
- publication year is the actual publication year;
- metrics bar is segmented and disappears when unmatched;
- `OpenAlex 引用 N` links to OpenAlex;
- citation copy returns GB/T text and localized feedback;
- mobile publication controls wrap without horizontal overflow.

- [ ] **Step 4: Confirm the GitHub Pages build path**

Because Ruby/Jekyll is unavailable locally, inspect `.github/workflows/pages.yml` and confirm it still runs `actions/jekyll-build-pages@v1`. The first pushed commit must be observed in GitHub Actions; deployment is complete only after the Pages build succeeds.

- [ ] **Step 5: Review only intended changes**

Run:

```powershell
git status --short
git diff --stat
git log --oneline --max-count=10
```

Expected: no temporary preview files or Python bytecode are staged; existing user changes remain preserved.

- [ ] **Step 6: Final implementation commit if verification fixes were required**

```powershell
git add --update
git commit -m "fix: complete publication feature verification"
```

Skip this commit when verification required no additional changes.
