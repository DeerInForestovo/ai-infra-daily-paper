#!/usr/bin/env python3
"""Generate the final bilingual index from selected candidates.

Usage:
    source .venv/bin/activate
    python generate_index.py --date 2026-06-25

Reads `YYYY-MM-DD_candidates.md` from the repo root, extracts papers marked with
`[x]`, fetches their metadata from arXiv, and writes `YYYY-MM-DD.md` (English
only). The agent should then translate the English abstracts into Chinese and
save the bilingual version back to `YYYY-MM-DD.md`. Finally, this script deletes
the temporary `YYYY-MM-DD_candidates.md` file.

To skip the deletion of the candidates file, pass `--keep-candidates`.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime

import arxiv


def parse_candidates(filepath: str) -> list[dict]:
    """Parse the candidates markdown file and return selected papers."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by "## " headers.
    sections = re.split(r"\n##\s+", content)
    selected = []

    for section in sections[1:]:  # skip header section
        lines = section.strip().splitlines()
        if not lines:
            continue

        # First line is like "1. [2606.27550v1](http://arxiv.org/abs/2606.27550v1)"
        header = lines[0]
        match = re.search(r"\[([^\]]+)\]", header)
        if not match:
            continue
        arxiv_id = match.group(1)

        # Check if selected.
        body = "\n".join(lines)
        if "- [x] Select" not in body and "- [X] Select" not in body:
            continue

        # Extract title.
        title_match = re.search(r"\*\*Title:\*\*\s*(.+)", body)
        title = title_match.group(1).strip() if title_match else ""

        # Extract categories.
        cat_match = re.search(r"\*\*Categories:\*\*\s*(.+)", body)
        categories = cat_match.group(1).strip() if cat_match else ""

        # Extract published date.
        pub_match = re.search(r"\*\*Published:\*\*\s*(.+)", body)
        published = pub_match.group(1).strip() if pub_match else ""

        # Extract abstract (between "### Abstract" and "---").
        abstract_match = re.search(r"### Abstract\s*\n\s*\n(.+?)\n\s*---", body, re.DOTALL)
        abstract = abstract_match.group(1).strip() if abstract_match else ""
        abstract = re.sub(r"\s+", " ", abstract)

        selected.append(
            {
                "arxiv_id": arxiv_id,
                "title": title,
                "categories": categories,
                "published": published,
                "abstract": abstract,
            }
        )

    return selected


def fetch_papers_by_id(ids: list[str]) -> list[arxiv.Result]:
    """Fetch paper metadata from arXiv by ID list."""
    if not ids:
        return []

    search = arxiv.Search(id_list=ids)
    client = arxiv.Client()
    papers: list[arxiv.Result] = []
    for result in client.results(search):
        papers.append(result)

    paper_by_id = {p.get_short_id(): p for p in papers}
    ordered = [paper_by_id[i] for i in ids if i in paper_by_id]
    missing = [i for i in ids if i not in paper_by_id]
    if missing:
        print(f"Warning: could not fetch {len(missing)} paper(s): {missing}")
    return ordered


def generate_index(
    selected: list[dict],
    target_date: str,
) -> str:
    """Generate the English index file and return its path."""
    filepath = f"{target_date}.md"

    ids = [p["arxiv_id"] for p in selected]
    papers = fetch_papers_by_id(ids)

    # Preserve order from selected.
    paper_by_id = {p.get_short_id(): p for p in papers}

    lines = [
        f"# AI Infra Papers – {target_date}",
        "",
        f"Target date: **{target_date}**",
        f"Total papers: **{len(selected)}**",
        "",
        "This index lists AI infrastructure related papers collected from arXiv.",
        "",
        "---",
        "",
    ]

    for i, candidate in enumerate(selected, start=1):
        arxiv_id = candidate["arxiv_id"]
        paper = paper_by_id.get(arxiv_id)

        title = candidate["title"] or (paper.title if paper else "")
        authors = [str(a) for a in paper.authors] if paper else []
        published = candidate["published"] or (
            paper.published.isoformat() if paper and paper.published else ""
        )
        categories = candidate["categories"] or (
            ", ".join(paper.categories) if paper else ""
        )
        abstract = candidate["abstract"] or (
            paper.summary.replace("\n", " ") if paper else ""
        )
        abstract = re.sub(r"\s+", " ", abstract)

        lines.extend(
            [
                f"## {i}. {title}",
                "",
                f"- **arXiv ID:** {arxiv_id}",
                f"- **Authors:** {', '.join(authors)}",
                f"- **Published:** {published}",
                f"- **Categories:** {categories}",
                f"- **arXiv URL:** http://arxiv.org/abs/{arxiv_id}",
                "",
                "### Abstract",
                "",
                abstract,
                "",
                "---",
                "",
            ]
        )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return filepath


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the final English index from selected candidates."
    )
    parser.add_argument(
        "--date",
        default="2026-06-25",
        help="Target date in YYYY-MM-DD format (default: 2026-06-25).",
    )
    parser.add_argument(
        "--keep-candidates",
        action="store_true",
        help="Keep the temporary candidates file instead of deleting it.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_date = args.date
    candidates_file = f"{target_date}_candidates.md"

    if not os.path.exists(candidates_file):
        print(f"Error: {candidates_file} not found. Run collect_candidates.py first.")
        return 1

    selected = parse_candidates(candidates_file)
    print(f"Selected {len(selected)} paper(s) from {candidates_file}")

    if not selected:
        print("No papers selected. Please mark papers with [x] in the candidates file.")
        return 0

    index_file = generate_index(selected, target_date)
    print(f"Generated English index: {index_file}")
    print("\nNext step: translate the English abstracts into Chinese and save the bilingual version.")

    if not args.keep_candidates:
        os.remove(candidates_file)
        print(f"Removed temporary file: {candidates_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
