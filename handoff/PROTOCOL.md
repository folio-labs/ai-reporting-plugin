# Agent Handoff Protocol

This directory is the shared communication channel between the Director (Claude Code),
Reporter (Gemini CLI), and Verifier (OpenAI Codex).

## Files

| File | Written by | Read by |
|------|-----------|---------|
| `reporter.md` | Director (task), Reporter (response) | Reporter, Director |
| `verifier.md` | Director (task), Verifier (response) | Verifier, Director |

## Frontmatter Fields

```yaml
task_id: 0<YYYYMMDD_HHMMSS>   # Set by Director when assigning a task
from:    director             # Always "director" for tasks
to:      reporter|verifier
status:  IDLE|PENDING|IN_PROGRESS|DONE|FAILED
updated: <ISO 8601 timestamp> # Updated by whoever last wrote to the file
```

## Status Lifecycle

```
IDLE → PENDING → IN_PROGRESS → DONE
                             → FAILED
```

- **Director** sets status to `PENDING` and writes the `## Task` section.
- **Agent** sets status to `IN_PROGRESS` when it starts work (optional).
- **Agent** sets status to `DONE` or `FAILED` and writes the `## Response` section.
- **Director** reads the response, then resets status to `IDLE`.

## Agent Responsibilities

### Reporter 
1. Poll `handoff/reporter.md` for `status: PENDING`.
2. Set status to `IN_PROGRESS`, run the requested skill script.
3. Write output (filename, row count, summary) to `## Response`.
4. Set status to `DONE` (or `FAILED` with error detail).

### Verifier
1. Poll `handoff/verifier.md` for `status: PENDING`.
2. Set status to `IN_PROGRESS`, run the verification task.
3. Write verification result to `## Response`.
4. Set status to `DONE` or `FAILED`.
5. If DONE, append a row to `reports/VERIFICATIONS.md`.

## Example Task (Director → Reporter)

```markdown
---
task_id: 20260319_143000
from: director
to: reporter
status: PENDING
updated: 2026-03-19T14:30:00Z
---

## Task

Run the checkout report.

    uv run skills/circ/checkout_report.py

Report back the output filename, row count, and any printed summary.

## Response

_Awaiting task._
```

## Notes

- This directory is git-tracked so changes are visible in `git log`.
- Do not put PII or credentials in these files.
- `reports/` is git-ignored; reference report filenames only.
