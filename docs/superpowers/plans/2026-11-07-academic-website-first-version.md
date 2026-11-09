# Academic Website First Version Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page bilingual academic homepage for Nan Zheng on GitHub Pages, with resume-backed sections and an automatically refreshed publication feed that the separate personal website can reuse.

**Architecture:** `zhengnan365.github.io` is the canonical Jekyll site and data source. The page keeps the existing Minimal Light identity/content layout, adds a fixed reference-style top navigation, and renders academic links as icon buttons below the avatar. A scheduled Python script queries OpenAlex by the canonical author ID, normalizes publications into `_data/publications.yml` and `assets/data/site-data.json`, then GitHub Pages rebuilds the page. The standalone personal website keeps its own visual shell and fetches the published JSON with a local fallback.

**Tech Stack:** Jekyll/Minimal Light, Markdown/Liquid, SCSS, vanilla JavaScript, Python standard library plus PyYAML, GitHub Actions, OpenAlex REST API.

**2026-11-07 visual revision:** Keep Minimal Light as the page shell. Reuse the fixed navy navigation implementation and the year-grouped publication components from `yaoyao-liu/personal-website`; do not use the earlier custom translucent navigation or the “latest eight + collapsed older papers” presentation.

---

### Task 1: Populate the Jekyll site configuration and single-page content

**Files:**
- Modify: `_config.yml`
- Modify: `index.md`
- Modify: `_layouts/homepage.html`
- Modify: `assets/css/style.scss`
- Copy: `assets/files/Zheng-Nan-CV-2026.docx`

- [ ] **Step 1: Replace placeholder identity values**

Set the site title, role, affiliation, email, ORCID, Scholar, Scopus, Web of Science, ResearchGate, CV path, canonical URL, and SEO description from the supplied resume and existing profile links.

- [ ] **Step 2: Add the single-page navigation and sections**

Create `#about`, `#research`, `#publications`, `#projects`, `#students`, `#awards`, and `#news` sections in `index.md`. Use resume text for the biography, two research directions, five projects, nine patents, eight awards, and a short student/supervision introduction. Keep papers rendered through the existing publications include.

- [ ] **Step 3: Add the fixed anchor navigation**

Add a compact `<nav class="site-nav">` to `_layouts/homepage.html` with links to the seven anchors and the CV. Keep it hidden or horizontally scrollable on small screens.

- [ ] **Step 4: Style the page for the approved one-page layout**

Append overrides in `assets/css/style.scss` for a navy/teal academic palette, section spacing, active anchor affordance, project/patent/award cards, and responsive navigation while preserving Minimal Light dark mode.

- [ ] **Step 5: Copy and link the resume**

Copy the provided DOCX to `assets/files/Zheng-Nan-CV-2026.docx` and expose it as the CV download link. Preserve the original source document in the personal website folder.

### Task 2: Create the publication data model and OpenAlex synchronizer

**Files:**
- Create: `_data/overrides.yml`
- Create: `scripts/sync_publications.py`
- Create: `assets/data/site-data.json`
- Replace: `_data/publications.yml`

- [ ] **Step 1: Define the canonical author configuration**

Use `A5001145059` and ORCID `0000-0002-2066-1506` as the only automated publication identity keys. Keep `overrides.yml` for `selected`, `highlight`, `display_authors`, and manual links.

- [ ] **Step 2: Implement the synchronizer**

The script requests `https://api.openalex.org/works?filter=authorships.author.id:A5001145059&per-page=100&sort=publication_date:desc`, follows pagination, deduplicates by DOI or OpenAlex ID, escapes text for YAML/JSON output, and writes the normalized records to both output files.

- [ ] **Step 3: Preserve manual overrides**

Merge override fields by DOI/OpenAlex ID after fetching. The script must retain records with missing DOI by using the OpenAlex ID as the stable key.

- [ ] **Step 4: Run the synchronizer locally**

Run `py scripts/sync_publications.py`, then verify that `_data/publications.yml` parses as YAML and `assets/data/site-data.json` parses as JSON. Confirm the output contains the latest Nan Zheng records and no duplicate DOI values.

### Task 3: Automate synchronization and Pages deployment

**Files:**
- Create: `.github/workflows/sync-publications.yml`
- Create: `.github/workflows/pages.yml`

- [ ] **Step 1: Add scheduled publication sync**

Run the sync workflow daily at a fixed UTC time and on `workflow_dispatch`; grant `contents: write`, commit changed generated files with `github-actions[bot]`, and skip the commit when no data changed.

- [ ] **Step 2: Add GitHub Pages deployment**

Use the official Pages artifact flow: checkout, `actions/jekyll-build-pages`, upload the Pages artifact, and deploy with `actions/deploy-pages`. Trigger on pushes to `main` and manual runs.

- [ ] **Step 3: Avoid workflow loops**

Keep the deployment workflow triggered by pushes, while the sync workflow only commits when generated output changes. Do not make the sync workflow depend on the deployment workflow.

### Task 4: Synchronize the standalone personal website

**Files:**
- Modify: `D:\00Keyan\18-课题组\个人网站\index.html`
- Create: `D:\00Keyan\18-课题组\个人网站\data\site-data.json`

- [ ] **Step 1: Add matching anchor sections**

Keep the existing language and theme controls, add the same seven section IDs, and place a publications container in the paper section.

- [ ] **Step 2: Fetch the GitHub Pages data feed**

Add a vanilla JavaScript loader that fetches `https://zhengnan365.github.io/assets/data/site-data.json` with a cache-busting query parameter, renders the first six publications, and falls back to `data/site-data.json` when the remote request fails.

- [ ] **Step 3: Keep the personal site lightweight**

Reuse the existing card style and only mirror the resume-backed sections; do not duplicate the OpenAlex fetching logic in this site.

### Task 5: Verify the first version

**Files:**
- Test: generated YAML/JSON, workflow YAML, and both HTML entry points

- [ ] **Step 1: Validate data files**

Run Python YAML/JSON parsing checks and a duplicate DOI check against `_data/publications.yml`.

- [ ] **Step 2: Validate links and anchors**

Search both HTML files for all navigation targets, the CV path, the JSON feed URL, and the six academic profile URLs.

- [ ] **Step 3: Inspect the rendered page**

Open the local `index.html` in a browser, verify navigation scrolling, language switching, dark mode, responsive layout, and publication fallback rendering.

- [ ] **Step 4: Review generated changes**

Run `git diff --check` in both repositories and inspect the final diff before committing the first version.

