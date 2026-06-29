# AGENTS.md — Project Context for AI Coding Agents

> This file is written for AI coding agents that work on this repository.
> It describes the project as it currently exists, not as it might become.

## Project Overview

The project collects AI infrastructure related papers from arXiv on a daily basis.
For each date, only a single bilingual Markdown file is kept in the repository root:
`YYYY-MM-DD.md`. No PDFs are stored locally.

- **Project name:** `ai-infra-paper`
- **Current state:** Refactored to root-level `.md` files only, no local PDFs
- **Known purpose:** Archive and index AI Infrastructure research, with a focus on
  deploying and optimizing open-source frameworks (e.g., vLLM) and open-source models
  (e.g., Qwen, or company-internal models fine-tuned from open-source checkpoints).

## Technology Stack

- **Language:** Python 3.10+
- **Dependencies:** `arxiv` (installed in `.venv`)
- **Virtual environment:** `.venv/`
- **Key files:**
  - `collect_candidates.py` — stage 1: fetch CS papers for an exact date and filter candidates
  - `generate_index.py` — stage 3: generate the English index and clean up temporary files

## Build and Test Commands

Activate the virtual environment before running scripts:

```bash
source .venv/bin/activate
```

### Stage 1: Generate candidates

```bash
python collect_candidates.py --date 2026-06-25
```

This creates a temporary file `2026-06-25_candidates.md` in the repo root.

### Stage 2: Agent review

Read `YYYY-MM-DD_candidates.md`, decide which papers are AI Infra related,
and mark selected papers by changing `- [ ] Select` to `- [x] Select`.

**Selection priority:** Prefer papers directly relevant to deploying and optimizing
open-source frameworks (e.g., vLLM) and open-source models (e.g., Qwen, or
company-internal models fine-tuned from open-source checkpoints). Focus on
inference acceleration, quantization, KV cache optimization, speculative decoding,
and serving systems. Avoid training-only optimizations, domain-specific applications,
and pure architecture papers without clear deployment benefits. Aim for 5-10
selected papers per day.

**Default next step:** After selecting papers, the agent should immediately
proceed to Stage 3 and Stage 4 automatically — generate the English index and
translate it into the bilingual `YYYY-MM-DD.md` — without asking the user for
confirmation.

### Stage 3: Generate English index

```bash
python generate_index.py --date 2026-06-25
```

This generates `2026-06-25.md` (English) in the repo root and removes the
temporary `2026-06-25_candidates.md` file.

### Stage 4: Translate to bilingual index

Read `YYYY-MM-DD.md` and add Chinese translations below each English abstract.
Save the bilingual version back to the same file. Keep the file in the repo root.

## Code Organization

```
.
├── AGENTS.md                  # This file
├── HOW_IT_WORKS.md            # Detailed workflow documentation
├── collect_candidates.py      # Stage 1 script
├── generate_index.py          # Stage 3 script
├── .venv/                     # Python virtual environment
├── 2026-06-25.md              # Example: final bilingual index
└── 2026-06-26.md              # Example: final bilingual index
```

## Code Style Guidelines

- Follow PEP 8 for Python code.
- Use type hints where reasonable.
- Keep scripts readable; prefer explicit over clever.
- When modifying keyword lists, prefer strong/technical AI Infra terms to reduce false positives.

## Testing Instructions

No automated tests exist. Verify a collection run by checking:

1. `YYYY-MM-DD_candidates.md` is generated and lists reasonable candidates.
2. After marking selections, `generate_index.py` produces `YYYY-MM-DD.md` in the repo root.
3. `YYYY-MM-DD.md` contains arXiv URLs and English abstracts for all selected papers.
4. The final `YYYY-MM-DD.md` provides bilingual title + abstract for each paper.

## Deployment Process

No deployment configuration is present. The project is intended to run locally
or in a personal cron job.

### Git workflow

The repository is managed with Git. When adding a new daily index:

1. Add only the new `YYYY-MM-DD.md` file.
2. Commit with the date as the message, e.g. `git commit -m "2026-06-30"`.
3. Push to the remote repository.

Do not commit temporary files such as `YYYY-MM-DD_candidates.md`, PDFs, or the
`.venv/` directory.

## Security Considerations

- Do not commit secrets, API keys, or private credentials.
- The script only contacts public arXiv endpoints.
- Be respectful of arXiv's rate limits.

## How to Update This File

Whenever significant files, build systems, or conventions are added to the project,
update this `AGENTS.md` to reflect the current architecture and workflow.
