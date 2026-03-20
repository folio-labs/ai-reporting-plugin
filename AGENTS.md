# Project Mandates: AI FOLIO Reporting

This document defines the foundational mandates, architectural patterns, and development standards for the SULFOLIO Reporting project. These instructions take absolute precedence over general defaults.

## Purpose

This project helps lirary staff generate custom circulation and inventory reports from FOLIO using AI coding assistants (Claude Code, Google Gemini CLI, OpenAI Codex). Staff describe the report they need in plain language; the agent writes and runs Python code against the FOLIO APIs.

## Core Principles

- **Data Privacy:** Never expose or log PII (patron names, barcodes, addresses) or FOLIO credentials. Credentials must always come from environment variables via `.env`.
- **Reliability:** Prioritize robust error handling for API integrations — FOLIO services may have varying latency or availability.
- **Transparency:** All data transformations must be well-documented and traceable back to source FOLIO records.

## Technical Standards

- **Language:** Python 3.12+
- **Package management:** All Python dependencies managed with `uv`. Use `uv add <package>` to add dependencies, `uv run <script>` to execute scripts, `uv sync` to install.
- **Style:** PEP 8. Use `ruff format` for formatting and `ruff check` for linting.
- **Testing:** Unit tests for all data processing logic. Integration tests for FOLIO API clients using mocks or `vcrpy`.

## FOLIO Client

The `folio_client.py` module exposes a single `get_client()` factory function that loads credentials from `.env` and returns an authenticated `FolioClient` instance. Always use this factory rather than instantiating `FolioClient` directly.

```python
from folio_client import get_client

fc = get_client()
```

### Credential Setup

Copy `.env.example` to `.env` and populate:

```
FOLIO_URL=https://your-folio-instance.example.edu
FOLIO_TENANT=your_tenant_id
FOLIO_USERNAME=your_username
FOLIO_PASSWORD=your_password
```

The `.env` file is git-ignored and must never be committed.

## FOLIO API Conventions

- Use `fc.folio_get_all(endpoint, key)` for paginated bulk retrieval.
- Use CQL queries for filtering: `query="status.name==\"Checked out\""`.
- Key endpoints:
  - Inventory: `/inventory/items`, `/inventory/instances`, `/inventory/holdings-storage/holdings`
  - Circulation: `/circulation/loans`, `/circulation/requests`
  - Users: `/users` (avoid fetching PII fields unless strictly necessary)

## Reporting Outputs

- Save report outputs to a `reports/` directory (git-ignored).
- Prefer CSV for tabular data; use `pandas` or the stdlib `csv` module.
- Always include a timestamp in output filenames, e.g. `overdue_loans_20260312.csv`.

## Independent Verification

To ensure accuracy when multiple AI agents (Claude Code, Gemini CLI, Codex) coordinate on FOLIO reports, follow these verification protocols:

1. **Peer Review:** One agent writes a report script; a second agent reviews the CQL queries and data mapping logic before execution.
2. **Blind Cross-Checks:** 
   - **Agent A:** Generates a report (e.g., `reports/overdue_loans_20260312.csv`).
   - **Agent B:** Writes a separate validation script to calculate totals, check for duplicates, or verify a random sample of UUIDs against the FOLIO API.
3. **Result Comparison:** If two agents generate the same report independently, their outputs must be bit-for-bit identical or reconcilable (e.g., if timestamps or row order differ).
4. **Verification Logs:** After a report is generated and verified, append a note to `reports/VERIFICATIONS.md` (git-ignored) with the report filename, the agents involved, and the verification outcome.

## Agent Roles

| Agent | Tool | Role |
|-------|------|------|
| Director | Claude Code | Receives staff requests, assigns tasks, synthesizes results |
| Reporter | Gemini CLI | Runs skill scripts, returns output filename + summary |
| Verifier | OpenAI Codex | Reviews report logic, runs verification scripts, logs to `reports/VERIFICATIONS.md` |

### Handoff Protocol

Agents communicate via files in `handoff/`. See `handoff/PROTOCOL.md` for the full spec.

- `handoff/reporter.md` — Director → Reporter task queue
- `handoff/verifier.md` — Director → Verifier task queue

Each file uses YAML frontmatter (`task_id`, `status`, `updated`) and two sections: `## Task` and `## Response`. Status lifecycle: `IDLE → PENDING → IN_PROGRESS → DONE|FAILED`.

## Documentation

- Keep `README.md` updated with setup instructions and high-level architecture.
- Use Google-style docstrings for all public functions and classes.
