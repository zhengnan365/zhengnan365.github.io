#!/usr/bin/env python3
"""Fetch Nan Zheng's OpenAlex works and publish website-friendly data."""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
AUTHOR_ID = os.environ.get("OPENALEX_AUTHOR_ID", "A5001145059")
ORCID = os.environ.get("ORCID", "0000-0002-2066-1506")
API_URL = "https://api.openalex.org/works"


def fetch_works() -> list[dict]:
    works: list[dict] = []
    cursor = "*"
    while cursor:
        query = urllib.parse.urlencode(
            {
                "filter": f"authorships.author.id:{AUTHOR_ID}",
                "per-page": "100",
                "sort": "publication_date:desc",
                "cursor": cursor,
                "select": "id,doi,title,publication_year,publication_date,type,authorships,primary_location,open_access,best_oa_location",
            }
        )
        request = urllib.request.Request(
            f"{API_URL}?{query}",
            headers={"User-Agent": "zhengnan365.github.io publication sync"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        for work in payload.get("results", []):
            works.append(work)
        cursor = payload.get("meta", {}).get("next_cursor")
        if not payload.get("results"):
            break
    return works


def stable_key(work: dict) -> str:
    return (work.get("doi") or work.get("id") or work.get("title") or "").lower().strip()


def normalize(work: dict) -> dict:
    source = (work.get("primary_location") or {}).get("source") or {}
    authors = []
    for authorship in work.get("authorships") or []:
        author = authorship.get("author") or {}
        name = author.get("display_name") or authorship.get("raw_author_name")
        if name:
            authors.append(name)
    oa = work.get("open_access") or {}
    best_oa = work.get("best_oa_location") or {}
    return {
        "id": work.get("id"),
        "doi": work.get("doi"),
        "title": work.get("title") or "Untitled work",
        "authors": ", ".join(authors),
        "venue": source.get("display_name") or "",
        "year": work.get("publication_year"),
        "date": work.get("publication_date"),
        "type": work.get("type"),
        "pdf": best_oa.get("pdf_url"),
        "url": (work.get("doi") or best_oa.get("landing_page_url") or work.get("id")),
        "open_access": bool(oa.get("is_oa")),
    }


def load_overrides() -> dict:
    path = ROOT / "_data" / "overrides.yml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_outputs(records: list[dict]) -> None:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    data = {
        "generated_at": generated_at,
        "source": "OpenAlex",
        "author_id": AUTHOR_ID,
        "orcid": ORCID,
        "publications": records,
    }
    yaml_path = ROOT / "_data" / "publications.yml"
    yaml_path.write_text(
        yaml.safe_dump({"main": records}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    json_path = ROOT / "assets" / "data" / "site-data.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    works = fetch_works()
    unique: dict[str, dict] = {}
    for work in works:
        key = stable_key(work)
        if key:
            unique[key] = normalize(work)
    overrides = load_overrides()
    records = []
    for record in sorted(unique.values(), key=lambda item: (item.get("year") or 0, item.get("date") or ""), reverse=True):
        override = overrides.get(record.get("doi") or record.get("id") or "", {})
        record.update(override)
        records.append(record)
    write_outputs(records)
    print(f"Wrote {len(records)} publications for {AUTHOR_ID}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
