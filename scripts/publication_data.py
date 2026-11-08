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


def normalize_work(
    work: dict[str, Any],
    owner_author_id: str,
    overrides: dict[str, dict[str, Any]],
    metrics: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Normalize one OpenAlex work into the website publication schema.

    ``overrides`` and ``metrics`` are accepted at this boundary so later
    synchronization steps can enrich the same record without changing the
    function signature.  Metric matching is intentionally handled by a later
    task; this first extraction step only carries publication metadata.
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
    }
    override = overrides.get(normalized_doi or "") or overrides.get(work.get("id") or "") or {}
    record["_exclude"] = bool(override.get("exclude"))
    record.update({key: value for key, value in override.items() if key != "exclude"})
    return record
