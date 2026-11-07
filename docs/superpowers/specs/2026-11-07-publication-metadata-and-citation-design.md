# Publication Metadata and Citation Design

**Date:** 2026-11-07

**Site:** `zhengnan365.github.io`
**Status:** Approved design, awaiting implementation plan

## 1. Objective

Extend the existing Jekyll/GitHub Pages academic website so that its publication list is automatically synchronized from OpenAlex and presents the metadata required for an academic homepage: corresponding authors, citation counts, journal metrics, and a copyable GB/T 7714—2015 citation.

The GitHub Pages site remains the canonical site and data publisher. The separate personal website consumes the generated JSON feed so that both sites show the same publication information.

## 2. Scope

This design covers:

- automatic OpenAlex publication synchronization;
- corresponding-author marking;
- OpenAlex citation counts;
- journal impact factor, CAS journal partition, TOP status, and JCR quartile;
- GB/T 7714—2015 citation generation and clipboard copying;
- publication presentation in Chinese and English modes;
- JSON synchronization to the separate personal website;
- failure handling and verification.

It does not include Scopus, Web of Science, ResearchGate scraping, automatic JCR data collection, or a multi-page conversion of the website.

## 3. Publication Source and Identity

OpenAlex is the sole automated publication and citation source for the first release.

The synchronizer queries works linked to OpenAlex author ID `A5001145059`. ORCID `0000-0002-2066-1506` remains stored as a secondary identity reference, but the publication query uses the OpenAlex author ID so that all works attached to the author profile can be retrieved.

Records are deduplicated using the normalized DOI when one exists. A normalized OpenAlex work ID is the fallback key for works without a DOI.

Because OpenAlex author disambiguation can occasionally attach an incorrect work or omit metadata, a small manual override file remains available. It may:

- exclude an incorrectly attached work;
- correct a display field;
- add or remove corresponding-author marks;
- supply a missing link or GB/T citation field.

The override file is an exception layer, not a separate publication database.

## 4. OpenAlex Synchronization

The synchronization script retrieves, at minimum, these OpenAlex work fields:

- OpenAlex work ID;
- DOI;
- title;
- publication date and publication year;
- work type;
- authorships, including raw author names and `is_corresponding`;
- corresponding author IDs;
- primary source and venue;
- bibliographic volume, issue, first page, and last page;
- `cited_by_count`;
- the canonical work URL.

The generated publication record contains:

- stable ID;
- title;
- ordered author list;
- formatted author HTML;
- corresponding-author presence;
- venue;
- publication year and date;
- volume, issue, and pages when available;
- DOI URL;
- OpenAlex URL;
- OpenAlex citation count and source label;
- GB/T 7714—2015 citation text;
- matched journal metrics.

The scheduled workflow runs weekly and can also be started manually. It writes both `_data/publications.yml` for Jekyll and `assets/data/site-data.json` for the separate website.

The synchronization job must not replace existing output with an empty or partial dataset when the OpenAlex request fails. It exits with an error and preserves the last successfully generated files.

## 5. Corresponding-Author Presentation

The synchronizer reads `authorships[].is_corresponding` from OpenAlex.

Every corresponding author is displayed with an asterisk directly after the name:

```text
Author A, Nan Zheng*, Author C
```

Nan Zheng remains bold wherever his OpenAlex author ID matches the configured author ID. Bold styling and the corresponding-author asterisk are independent, so a corresponding author may be both bold and marked with `*`.

No separate legend is added below the authors; the approved presentation is the compact `姓名*` form only.

When OpenAlex does not provide corresponding-author information, the site does not infer it from author order, email position, or any other heuristic. No mark is shown unless the OpenAlex data or a manual override explicitly identifies a corresponding author.

## 6. Publication Item Layout

Publications remain grouped by their actual publication year. The year shown beside the journal is the work's publication year, not the metric year.

Each publication item displays, in order:

1. original-language publication title;
2. ordered authors, with Nan Zheng bolded and corresponding authors marked as `姓名*`;
3. a segmented journal-metrics bar when reliable metrics exist;
4. original journal or conference name and actual publication year;
5. action buttons for DOI, OpenAlex citations, and citation copying.

Publication thumbnails are removed. PDF and Open Access buttons are removed. Publication titles, author names, and venue names remain in their original language and are not translated by the language toggle.

## 7. Journal Metrics

Journal metrics are maintained in `_data/journal_metrics.yml`, separate from OpenAlex-generated publication data. This prevents synchronization from overwriting curated or licensed metric information.

Entries should be matched primarily by ISSN-L or ISSN. A normalized journal title may be used as a documented fallback where an ISSN is unavailable.

Each entry may include:

- metric edition or year;
- Journal Impact Factor;
- CAS partition;
- CAS TOP status;
- JCR quartile.

The visual format is the approved segmented bar, for example:

```text
影响因子 11.2 | 中科院 1区 TOP | JCR Q1
```

English mode changes only the labels, for example:

```text
Impact Factor 11.2 | CAS Zone 1 TOP | JCR Q1
```

For TOP journals, the Chinese text is exactly `中科院 1区 TOP` when the configured partition is Zone 1. The actual partition value determines the displayed zone.

If a publication has no reliable journal-metric record, the entire metrics bar is omitted. Missing individual values are not guessed. The metric edition is stored in data even when it is not printed in every publication row.

## 8. Citation Count

The citation count is taken from OpenAlex `cited_by_count` and is explicitly attributed in the interface:

- Chinese: `OpenAlex 引用 N`
- English: `N OpenAlex citations`

The citation control links to the associated OpenAlex work page. Citation counts from OpenAlex, Scopus, Web of Science, Google Scholar, and ResearchGate are not combined because their coverage and counting rules differ.

The data model keeps citation source, count, URL, and synchronization time as separate fields so that a future Scopus or Web of Science provider can be added without redesigning the publication component.

## 9. GB/T 7714—2015 Citation Copying

The synchronization script builds a plain-text GB/T 7714—2015 citation from the best available metadata. For a journal article, the intended structure is:

```text
作者. 题名[J]. 期刊名, 年, 卷(期): 起止页码. DOI.
```

The formatter omits unavailable optional elements without leaving duplicate punctuation or empty parentheses. It preserves the publication's original title, author names, and venue name.

The publication row includes a button:

- Chinese: `引用`
- English: `Cite`

Clicking it copies the stored citation text through the Clipboard API. On success, the button temporarily changes to `已复制` or `Copied`. If the Clipboard API is unavailable, a hidden textarea fallback performs the copy. A failed copy changes the label to `复制失败` or `Copy failed` without breaking other page interactions.

## 10. Language, Theme, and Visual Integration

The site remains a single-page Minimal Light website with the fixed navy navigation bar. Chinese is the default language and light mode is the default theme.

The top-right controls switch language and light/dark mode. Translated interface strings include navigation labels, section labels, metric labels, citation labels, and copy feedback. Publication bibliographic content is not translated.

The avatar retains the approved soft shadow. Publication controls and the segmented metrics bar must have accessible contrast in both themes and remain usable on a 390-pixel-wide mobile viewport.

## 11. Shared Data Feed

`assets/data/site-data.json` is the public data contract between the GitHub Pages site and the separate personal website.

The feed includes:

- generation time;
- OpenAlex author ID and ORCID;
- source name;
- all normalized publication records;
- citation metadata;
- corresponding-author information;
- journal metrics;
- preformatted GB/T citation text.

The separate personal website fetches this JSON and renders the shared publication fields in its own visual shell. If the remote request fails, it may use a local cached copy. It does not query OpenAlex independently.

## 12. Error Handling

- Network or OpenAlex API failure: stop synchronization and retain the last valid generated files.
- Empty API response: treat it as an error rather than publishing an empty list.
- Duplicate DOI: keep one normalized record and report the duplicate during synchronization.
- Missing DOI: use the OpenAlex work ID as the stable identifier.
- Missing corresponding-author data: show no asterisk and make no inference.
- Missing journal metrics: omit the complete metric bar.
- Missing citation count: omit the citation-count control rather than displaying a misleading zero.
- Clipboard failure: show localized failure feedback while retaining the citation text in page data.
- Invalid manual override: fail validation before generated files are replaced.

## 13. Verification Strategy

The implementation plan must include automated or scripted checks for:

- YAML and JSON parsing;
- duplicate DOI detection;
- preservation of existing output after a simulated API failure;
- a single corresponding author;
- multiple corresponding authors;
- a work without corresponding-author metadata;
- Nan Zheng as a bold corresponding author;
- GB/T citation formatting with complete and partial bibliographic data;
- journal metric matching and omission when unmatched;
- localized Chinese and English labels;
- citation copy success and fallback behavior;
- desktop and 390-pixel mobile layouts;
- light and dark theme contrast;
- remote JSON loading and local fallback on the separate website.

Because Ruby/Jekyll is not currently installed locally, static validation and browser preview remain acceptable during development, but the GitHub Pages workflow must perform the real Jekyll build before deployment.

## 14. Future Extension Points

The first release uses OpenAlex only. Future Scopus or Web of Science support may add another citation provider while keeping provider name, count, URL, and update time explicit. ResearchGate remains an outbound profile link and is not scraped.

No future provider is required for this implementation, and no current interface should imply that OpenAlex citation counts are equivalent to counts from another database.
