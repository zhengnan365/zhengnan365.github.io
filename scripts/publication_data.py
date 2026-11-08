"""Pure helpers for normalizing OpenAlex publication records.

The synchronization script is responsible for fetching records and writing
files.  This module keeps the publication-domain transformations independent
of the network and filesystem so they can be tested with small fixtures.
"""

from __future__ import annotations

import html
import re
from typing import Any


def short_openalex_id(value: str | None) -> str:
    """Return the final identifier component from an OpenAlex URL or ID."""

    return (value or "").rstrip("/").rsplit("/", 1)[-1]


def normalize_doi(value: str | None) -> str | None:
    """Normalize a DOI to its lowercase identifier form.

    OpenAlex normally returns a ``https://doi.org/...`` URL, but overrides and
    hand-authored data may use ``doi:`` or the resolver-less form.  Empty
    values are represented as ``None`` so callers can distinguish missing
    metadata from a real DOI.
    """

    if not value:
        return None
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    return doi.lower() or None


def doi_url(value: str | None) -> str | None:
    """Return a canonical DOI resolver URL, or ``None`` for missing values."""

    doi = normalize_doi(value)
    return f"https://doi.org/{doi}" if doi else None


def build_author_fields(
    authorships: list[dict[str, Any]], owner_author_id: str
) -> tuple[str, str, bool]:
    """Build plain/display author strings and detect corresponding authors.

    Author ownership is identified by the OpenAlex author ID.  Display names
    are escaped before the owner's name is wrapped in ``<strong>`` so metadata
    from the API cannot inject markup into the rendered page.
    """

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


def match_metrics(
    source: dict[str, Any], metrics: dict[str, dict[str, Any]]
) -> dict[str, Any] | None:
    """Return the curated metric entry matching a journal source.

    OpenAlex provides a stable ISSN-L plus one or more edition-specific ISSNs.
    The ISSN-L is preferred so a journal's metric stays consistent when an
    article is indexed under a print or electronic ISSN.  The edition ISSNs
    are retained as a fallback for sources whose ISSN-L is missing or differs
    from the curated key.
    """

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


def _citation_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def page_range(first_page: str | None, last_page: str | None) -> str | None:
    """Return a compact page range, omitting duplicate or missing endpoints."""

    first = _citation_text(first_page)
    last = _citation_text(last_page)
    if first and last and first != last:
        return f"{first}-{last}"
    return first or last


def format_gbt7714(record: dict[str, Any]) -> str:
    """Format a normalized record as a GB/T 7714-2015 journal citation."""

    type_mark = "J" if record.get("type") in {"article", "review"} else "C"
    authors = _citation_text(record.get("authors")).replace("*", "").strip()
    title = _citation_text(record.get("title")) or "Untitled work"
    lead = f"{authors}. " if authors else ""
    parts = [f"{lead}{title}[{type_mark}]."]

    publication_segments: list[str] = []
    venue = _citation_text(record.get("venue"))
    if venue:
        publication_segments.append(venue)
    year = _citation_text(record.get("year"))
    if year:
        publication_segments.append(year)

    volume = _citation_text(record.get("volume"))
    issue = _citation_text(record.get("issue"))
    volume_issue = volume
    if volume and issue:
        volume_issue += f"({issue})"
    if volume_issue:
        publication_segments.append(volume_issue)

    pages = page_range(record.get("first_page"), record.get("last_page"))
    if pages:
        if publication_segments:
            publication_segments[-1] += f": {pages}"
        else:
            publication_segments.append(pages)
    publication = ", ".join(publication_segments)
    if publication:
        parts.append(f" {publication}.")
    normalized_doi = normalize_doi(record.get("doi"))
    if normalized_doi:
        parts.append(f" DOI: {normalized_doi}.")
    return "".join(parts)


def normalize_work(
    work: dict[str, Any],
    owner_author_id: str,
    overrides: dict[str, dict[str, Any]],
    metrics: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Normalize one OpenAlex work into the website publication schema.

    ``overrides`` and ``metrics`` enrich the same normalized record before
    it is returned to the synchronization layer.
    """

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
        "metrics": match_metrics(source, metrics),
    }
    override = overrides.get(normalized_doi or "") or overrides.get(work.get("id") or "") or {}
    record["_exclude"] = bool(override.get("exclude"))
    record.update({key: value for key, value in override.items() if key != "exclude"})
    record["citation_gbt7714"] = record.get("citation_gbt7714") or format_gbt7714(record)
    return record
