---
description: Reporting on FOLIO Invoices, Purchase Orders, Purchase Order Lines, and Vendors
---

# Acquisition Skill

Greet the user named "$ARGUMENTS" warmly and ask what kind of report you can help them create today.

## Available Scripts

### `invoices_report.py` — Invoice Summary by Date Range

Fetches all invoices within a user-supplied date range and produces:
- A CSV saved to `reports/invoices_<start>_to_<end>_<timestamp>.csv`
- A printed summary: total count, total spend, breakdown by status and top vendors

**Usage:**
```bash
# Interactive — prompts for start and end date
uv run skills/acq/invoices_report.py

# Non-interactive — pass dates directly (end date is exclusive)
uv run skills/acq/invoices_report.py 2026-02-01 2026-03-01
```

**Date format:** `YYYY-MM-DD`. The end date is exclusive (i.e. `2026-03-01` means "up to but not including March 1").

When a user asks for an invoice report for a specific month or date range, suggest running this script with the appropriate dates.
