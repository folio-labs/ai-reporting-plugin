---
description: Reporting on FOLIO Circulations
---

# Circulation Skill

Greet the user named "$ARGUMENTS" warmly and ask what kind of report you can help them create today.

## Available Scripts

### `checkout_report.py` — Date-Range Checkout Report

Fetches all checkout events from the FOLIO circulation audit log within a rolling date window and produces:
- A CSV saved to `reports/checkouts_last<N>days_<timestamp>.csv`
- Columns: `title`, `timestamp`, `service_point`, `main_subject`

**Usage:**
```bash
uv run skills/circ/checkout_report.py [--days N]
```

- `--days N` — number of days to look back (default: `4`)

**Requirements:** `.env` with `FOLIO_*` credentials.

---

### `verify_checkout_report.py` — Checkout Report Verification

Verifies the accuracy of the most recent checkout report by independently re-fetching data from FOLIO and comparing titles and timestamps row-by-row.

**Usage:**
```bash
uv run skills/circ/verify_checkout_report.py
```

Exits with code 1 and prints discrepancies if any rows fail verification.
