#!/usr/bin/env python3
"""Fetch CS-category papers from arXiv for a given date and filter AI Infra candidates.

Usage:
    source .venv/bin/activate
    python collect_candidates.py --date 2026-06-25

The script searches arXiv's CS categories for papers submitted on the exact date,
then filters candidates whose title or abstract contains AI Infra related keywords.
Results are written to the repository root as `YYYY-MM-DD_candidates.md` for agent
review. After the agent marks selected papers with `[x]`, `generate_index.py` reads
this file and produces the final bilingual `YYYY-MM-DD.md`.
"""

from __future__ import annotations

import argparse
import os
import re
from datetime import datetime, timedelta

import arxiv

# CS categories to scan.
CS_CATEGORIES = [
    "cs.LG",  # Machine Learning
    "cs.CL",  # Computation and Language
    "cs.AI",  # Artificial Intelligence
    "cs.AR",  # Hardware Architecture
    "cs.DC",  # Distributed, Parallel, and Cluster Computing
    "cs.SE",  # Software Engineering
    "cs.OS",  # Operating Systems
    "cs.DB",  # Databases
    "cs.NE",  # Neural and Evolutionary Computing
    "cs.CV",  # Computer Vision and Pattern Recognition
]

# AI Infra related keywords for coarse filtering.
# Only strong/technical keywords are kept to reduce false positives.
INFRA_KEYWORDS = [
    # Inference acceleration
    "inference acceleration",
    "inference optimization",
    "decoding acceleration",
    "fast inference",
    "efficient inference",
    "low-latency inference",
    "throughput optimization",
    # Speculative / parallel decoding
    "speculative decoding",
    "multi-token prediction",
    "self-speculative decoding",
    "draft model",
    "look-ahead decoding",
    # Model compression & quantization
    "quantization",
    "pruning",
    "sparsity",
    "model compression",
    "knowledge distillation",
    "AWQ",
    "GPTQ",
    "post-training quantization",
    # Memory and caching
    "KV cache",
    "paged attention",
    "memory efficient",
    "activation checkpointing",
    "offloading",
    # Parallelism & distributed systems
    "model parallelism",
    "tensor parallelism",
    "pipeline parallelism",
    "distributed training",
    "distributed inference",
    "mixture of experts",
    "MoE",
    # Training efficiency
    "training efficiency",
    "gradient compression",
    "zero redundancy optimizer",
    "federated learning",
    # Attention / long context
    "long context",
    "efficient attention",
    "linear attention",
    "sliding window attention",
    "context length extrapolation",
]


def make_date_filter(target_date: str) -> str:
    """Return an arXiv submittedDate range for the exact date."""
    target = datetime.strptime(target_date, "%Y-%m-%d")
    start = target.strftime("%Y%m%d%H%M")
    end = (target + timedelta(days=1)).strftime("%Y%m%d%H%M")
    return f"[{start} TO {end}]"


def match_keywords(text: str) -> list[str]:
    """Return the list of matched AI Infra keywords (case-insensitive)."""
    text_lower = text.lower()
    matched = []
    for kw in INFRA_KEYWORDS:
        if kw.lower() in text_lower:
            matched.append(kw)
    return matched


def fetch_cs_papers(target_date: str, max_results: int = 2000) -> list[arxiv.Result]:
    """Fetch all CS papers submitted on the exact target date."""
    cat_query = " OR ".join(f"cat:{c}" for c in CS_CATEGORIES)
    date_filter = make_date_filter(target_date)
    search_query = f"({cat_query}) AND submittedDate:{date_filter}"

    print(f"Query: {search_query}")
    print(f"Max results: {max_results}")

    search = arxiv.Search(
        query=search_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    client = arxiv.Client()
    papers: list[arxiv.Result] = []
    for result in client.results(search):
        papers.append(result)
    return papers


def generate_candidates_file(
    papers: list[arxiv.Result],
    target_date: str,
) -> str:
    """Generate YYYY-MM-DD_candidates.md in the repo root and return its path."""
    filepath = f"{target_date}_candidates.md"

    # Filter candidates.
    candidates = []
    for paper in papers:
        title = paper.title or ""
        summary = paper.summary or ""
        combined = f"{title} {summary}"
        matched = match_keywords(combined)
        if matched:
            candidates.append((paper, matched))

    # Sort by number of matched keywords (desc) then by arxiv id.
    candidates.sort(key=lambda x: (-len(x[1]), x[0].get_short_id()))

    lines = [
        f"# AI Infra Candidate Papers – {target_date}",
        "",
        f"Target date: **{target_date}**",
        f"Total CS papers on this date: **{len(papers)}**",
        f"Candidate papers after keyword filtering: **{len(candidates)}**",
        "",
        "Instructions: Review each candidate and decide whether it is related to AI Infrastructure "
        "(inference/training acceleration, model compression, distributed systems, memory optimization, "
        "serving systems, etc.).",
        "",
        "To select a paper, change `[ ]` to `[x]` next to its arXiv ID.",
        "Then run `python generate_index.py --date YYYY-MM-DD` to produce the final bilingual index.",
        "",
        "---",
        "",
    ]

    for i, (paper, matched) in enumerate(candidates, start=1):
        arxiv_id = paper.get_short_id()
        title = paper.title.replace("\n", " ")
        summary = paper.summary.replace("\n", " ")
        categories = ", ".join(paper.categories)
        published = paper.published.isoformat() if paper.published else ""

        lines.extend(
            [
                f"## {i}. [{arxiv_id}](http://arxiv.org/abs/{arxiv_id})",
                "",
                f"- [ ] Select",
                f"- **Title:** {title}",
                f"- **Categories:** {categories}",
                f"- **Published:** {published}",
                f"- **Matched keywords:** {', '.join(matched)}",
                "",
                "### Abstract",
                "",
                summary,
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
        description="Fetch CS papers from arXiv for a given date and filter AI Infra candidates."
    )
    parser.add_argument(
        "--date",
        default="2026-06-25",
        help="Target date in YYYY-MM-DD format (default: 2026-06-25).",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=2000,
        help="Maximum number of papers to fetch (default: 2000).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_date = args.date

    print(f"Fetching CS papers for {target_date} ...")
    papers = fetch_cs_papers(target_date, max_results=args.max_results)
    print(f"Found {len(papers)} CS papers on {target_date}.")

    filepath = generate_candidates_file(papers, target_date)
    print(f"Candidates written to: {filepath}")

    if not papers:
        print(
            f"\nNo CS papers found on {target_date}. "
            "This is expected if the date is on a weekend or in the future. Try a different date."
        )
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
