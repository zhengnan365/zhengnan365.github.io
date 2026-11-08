#!/usr/bin/env python3
"""Fetch Nan Zheng's OpenAlex works and publish website-friendly data."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.publication_data import normalize_doi, normalize_work, short_openalex_id
except ModuleNotFoundError:  # pragma: no cover - supports direct script execution
    from publication_data import normalize_doi, normalize_work, short_openalex_id


ROOT = Path(__file__).resolve().parents[1]
AUTHOR_ID = os.environ.get("OPENALEX_AUTHOR_ID", "A5001145059")
ORCID = os.environ.get("ORCID", "0000-0002-2066-1506")
API_URL = "https://api.openalex.org/works"
SELECT_FIELDS = ",".join(
    [
        "id",
        "doi",
        "title",
        "publication_year",
        "publication_date",
        "type",
        "authorships",
        "corresponding_author_ids",
        "primary_location",
        "biblio",
        "cited_by_count",
        "open_access",
        "best_oa_location",
    ]
)

VENUE_ABBREVIATIONS = {
    "Applied Energy": "Applied Energy",
    "Applied Thermal Engineering": "ATE",
    "Energy": "Energy",
    "Energy Conversion and Management": "ECM",
    "Fuel": "Fuel",
    "International Journal of Hydrogen Energy": "IJHE",
    "Journal of Energy Storage": "JES",
    "Journal of Mechanical Science and Technology": "JMST",
    "Journal of Thermal Science": "JTS",
    "Physics of Fluids": "PoF",
    "Renewable Energy": "RE",
    "Renewable and Sustainable Energy Reviews": "RSER",
    "Science China Technological Sciences": "SCTS",
    "SSRN Electronic Journal": "Preprint",
    "Sustainable Energy Technologies and Assessments": "SETA",
}

OVERRIDE_TYPES: dict[str, tuple[type, ...]] = {
    "exclude": (bool,),
    "stable_id": (str,),
    "id": (str,),
    "doi": (str, type(None)),
    "title": (str,),
    "authors": (str,),
    "display_authors": (str,),
    "has_corresponding_author": (bool,),
    "venue": (str,),
    "issn_l": (str, type(None)),
    "issns": (list, type(None)),
    "year": (int, type(None)),
    "date": (str, type(None)),
    "type": (str, type(None)),
    "volume": (str, type(None)),
    "issue": (str, type(None)),
    "first_page": (str, type(None)),
    "last_page": (str, type(None)),
    "url": (str, type(None)),
    "openalex_url": (str, type(None)),
    "citation_count": (int, type(None)),
    "citation_source": (str,),
    "citation_gbt7714": (str,),
    "metrics": (dict, type(None)),
    "conference": (str,),
    "conference_short": (str,),
    "pdf": (str, type(None)),
    "open_access": (bool,),
    "image": (str,),
}


def fetch_works() -> list[dict]:
    """Fetch all works for the configured OpenAlex author."""

    works: list[dict] = []
    cursor = "*"
    expected_count: int | None = None
    while cursor:
        query = urllib.parse.urlencode(
            {
                "filter": f"authorships.author.id:{AUTHOR_ID}",
                "per-page": "100",
                "sort": "publication_date:desc",
                "cursor": cursor,
                "select": SELECT_FIELDS,
            }
        )
        request = urllib.request.Request(
            f"{API_URL}?{query}",
            headers={"User-Agent": "zhengnan365.github.io publication sync"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        if not isinstance(payload, dict):
            raise RuntimeError("OpenAlex returned a malformed page; preserving previous generated data")
        meta = payload.get("meta") or {}
        if not isinstance(meta, dict):
            raise RuntimeError("OpenAlex returned malformed pagination metadata")
        if meta.get("count") is None:
            raise RuntimeError("OpenAlex omitted its result count; preserving previous generated data")
        try:
            page_count = int(meta["count"])
        except (TypeError, ValueError) as error:
            raise RuntimeError("OpenAlex returned an invalid result count") from error
        if page_count < 0:
            raise RuntimeError("OpenAlex returned a negative result count")
        if expected_count is None:
            expected_count = page_count
        elif page_count != expected_count:
            raise RuntimeError("OpenAlex returned inconsistent result counts")
        results = payload.get("results")
        if not isinstance(results, list) or not results:
            raise RuntimeError(
                "OpenAlex returned an empty or malformed page; preserving previous generated data"
            )
        works.extend(results)
        cursor = meta.get("next_cursor")
    if expected_count is not None and len(works) != expected_count:
        raise RuntimeError(
            f"OpenAlex returned {len(works)} of {expected_count} works; preserving previous generated data"
        )
    return works


def venue_abbreviation(venue: str, work_type: str | None) -> str:
    if venue in VENUE_ABBREVIATIONS:
        return VENUE_ABBREVIATIONS[venue]
    if work_type == "conference-paper":
        return "Conference"
    if work_type == "preprint":
        return "Preprint"
    return venue[:18] if venue else "Publication"


def validate_overrides(overrides: dict[str, dict[str, Any]]) -> None:
    """Reject unknown override fields and values with the wrong type."""

    if not isinstance(overrides, dict):
        raise ValueError("Publication overrides must be a YAML mapping")
    for identifier, values in overrides.items():
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("Publication override keys must be non-empty strings")
        normalized_identifier = normalize_doi(identifier)
        valid_doi = normalized_identifier == identifier and bool(
            re.fullmatch(r"10\.\d{4,9}/\S+", identifier)
        )
        valid_openalex = bool(
            re.fullmatch(r"https://openalex\.org/W\d+", identifier)
        )
        if not (valid_doi or valid_openalex):
            raise ValueError(
                f"Override key {identifier!r} must be a normalized DOI or full OpenAlex work ID"
            )
        if not isinstance(values, dict):
            raise ValueError(f"Override {identifier!r} must be a mapping")
        unknown = set(values) - set(OVERRIDE_TYPES)
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"Override {identifier!r} has unsupported field(s): {names}")
        for field, value in values.items():
            expected = OVERRIDE_TYPES[field]
            invalid_bool_for_int = field in {"year", "citation_count"} and isinstance(value, bool)
            if invalid_bool_for_int or not isinstance(value, expected):
                names = ", ".join(item.__name__ for item in expected)
                raise ValueError(
                    f"Override {identifier!r} field {field!r} must be {names}"
                )


def normalize(
    work: dict,
    overrides: dict[str, dict[str, Any]] | None = None,
    metrics: dict[str, dict[str, Any]] | None = None,
) -> dict:
    """Normalize a work and retain the site's existing presentation fields."""

    # Some OpenAlex responses expose corresponding authors only through the
    # work-level ``corresponding_author_ids`` list.  Fold that signal into the
    # per-authorship shape consumed by publication_data without mutating the
    # fetched payload.
    corresponding_ids = {
        short_openalex_id(value)
        for value in (work.get("corresponding_author_ids") or [])
        if value
    }
    if corresponding_ids:
        normalized_work = dict(work)
        normalized_authorships = []
        for authorship in work.get("authorships") or []:
            item = dict(authorship)
            author = item.get("author") or {}
            if short_openalex_id(author.get("id")) in corresponding_ids:
                item["is_corresponding"] = True
            normalized_authorships.append(item)
        normalized_work["authorships"] = normalized_authorships
    else:
        normalized_work = work
    record = normalize_work(normalized_work, AUTHOR_ID, overrides or {}, metrics or {})
    source = (work.get("primary_location") or {}).get("source") or {}
    venue = source.get("display_name") or ""
    work_type = work.get("type")
    # Keep the existing presentation fields until the publication component
    # removes the legacy PDF/Open Access controls. Explicit override values
    # retain precedence over these derived defaults.
    oa = work.get("open_access") or {}
    best_oa = work.get("best_oa_location") or {}
    record.setdefault("conference", venue)
    record.setdefault("conference_short", venue_abbreviation(venue, work_type))
    record.setdefault("pdf", best_oa.get("pdf_url"))
    record.setdefault("url", record.get("doi") or best_oa.get("landing_page_url") or work.get("id"))
    record.setdefault("open_access", bool(oa.get("is_oa")))
    record.setdefault("image", "assets/img/pub-placeholder.svg")
    return record


def _load_mapping(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    if any(not isinstance(value, dict) for value in payload.values()):
        raise ValueError(f"Expected mapping values in {path}")
    return payload


def load_overrides(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    """Load manually curated publication overrides."""

    overrides = _load_mapping(root / "_data" / "overrides.yml")
    validate_overrides(overrides)
    return overrides


def load_metrics(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    """Load curated journal metrics keyed by ISSN-L/ISSN."""

    return _load_mapping(root / "_data" / "journal_metrics.yml")


def build_records(
    works: list[dict],
    overrides: dict[str, dict[str, Any]],
    metrics: dict[str, dict[str, Any]],
) -> list[dict]:
    """Normalize, filter, deduplicate, and sort fetched works.

    An empty response is treated as a failed synchronization.  Raising before
    output generation leaves the previous generated files untouched.
    """

    if not works:
        raise RuntimeError("OpenAlex returned no works; preserving previous generated data")
    validate_overrides(overrides)

    unique: dict[str, dict] = {}
    duplicate_count = 0
    for work in works:
        record = normalize(work, overrides, metrics)
        if record.pop("_exclude", False):
            continue
        key = record.get("stable_id")
        if key:
            if key in unique:
                duplicate_count += 1
                print(
                    f"Warning: replacing duplicate publication stable_id {key}",
                    file=sys.stderr,
                )
            unique[key] = record
    if not unique:
        raise RuntimeError("No valid publications remained after normalization")
    if duplicate_count:
        print(f"Warning: replaced {duplicate_count} duplicate publication(s)", file=sys.stderr)
    return sorted(
        unique.values(),
        key=lambda item: (item.get("year") or 0, item.get("date") or ""),
        reverse=True,
    )


def _stage_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.write_text(content, encoding="utf-8")
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def atomic_write_batch(files: dict[Path, str]) -> None:
    """Atomically replace several files, rolling back if any replacement fails."""

    staged: list[tuple[Path, Path]] = []
    transactions: list[tuple[Path, Path | None]] = []
    rollback_failures: list[tuple[Path, Path, OSError]] = []
    try:
        for path, content in files.items():
            path = Path(path)
            staged.append((path, _stage_file(path, content)))
        for path, temporary in staged:
            backup: Path | None = None
            if path.exists():
                descriptor, backup_name = tempfile.mkstemp(
                    prefix=f".{path.name}.", suffix=".bak", dir=path.parent
                )
                os.close(descriptor)
                backup = Path(backup_name)
                backup.unlink(missing_ok=True)
                os.replace(path, backup)
            transactions.append((path, backup))
            os.replace(temporary, path)
    except BaseException as error:
        # Restore every destination whose original was moved aside.  A
        # destination with no original is removed if its replacement landed.
        for path, backup in reversed(transactions):
            try:
                path.unlink(missing_ok=True)
                if backup is not None and backup.exists():
                    os.replace(backup, path)
            except OSError as rollback_error:
                # Keep a failed backup on disk so the previous feed can be
                # recovered manually, and surface its path to the caller.
                if backup is not None:
                    rollback_failures.append((path, backup, rollback_error))
        if rollback_failures:
            details = "; ".join(
                f"{path}: backup preserved at {backup} ({rollback_error})"
                for path, backup, rollback_error in rollback_failures
            )
            raise RuntimeError(f"Publication feed rollback failed; {details}") from error
        raise
    finally:
        for _, temporary in staged:
            temporary.unlink(missing_ok=True)
        for _, backup in transactions:
            if backup is not None and all(item[1] != backup for item in rollback_failures):
                backup.unlink(missing_ok=True)


def atomic_write(path: Path, content: str) -> None:
    """Replace one file atomically (compatibility wrapper)."""

    atomic_write_batch({Path(path): content})


def _generated_at(records: list[dict], json_path: Path) -> str:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if not json_path.exists():
        return generated_at
    try:
        existing = json.loads(json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return generated_at
    if existing.get("publications") == records and existing.get("generated_at"):
        return existing["generated_at"]
    return generated_at


def write_outputs(records: list[dict], root: Path = ROOT) -> None:
    """Validate and atomically write identical YAML and JSON publication lists."""

    root = Path(root)
    yaml_path = root / "_data" / "publications.yml"
    json_path = root / "assets" / "data" / "site-data.json"
    generated_at = _generated_at(records, json_path)
    payload = {
        "generated_at": generated_at,
        "source": "OpenAlex",
        "author_id": AUTHOR_ID,
        "orcid": ORCID,
        "publications": records,
    }
    yaml_content = yaml.safe_dump(
        {"main": records}, allow_unicode=True, sort_keys=False
    )
    json_content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    # Parse and compare the serialized values before either destination is
    # replaced.  This catches serializer regressions without touching data.
    parsed_yaml = yaml.safe_load(yaml_content)
    parsed_json = json.loads(json_content)
    if not isinstance(parsed_yaml, dict) or parsed_yaml.get("main") != records:
        raise ValueError("Generated YAML records failed validation")
    if parsed_json.get("publications") != records:
        raise ValueError("Generated JSON records failed validation")

    atomic_write_batch({yaml_path: yaml_content, json_path: json_content})


def main() -> int:
    works = fetch_works()
    overrides = load_overrides()
    metrics = load_metrics()
    records = build_records(works, overrides, metrics)
    write_outputs(records)
    print(f"Wrote {len(records)} publications for {AUTHOR_ID}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
