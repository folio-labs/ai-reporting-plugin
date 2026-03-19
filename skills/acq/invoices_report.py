"""Invoice Summary Report.

Fetches all invoices within a given date range and produces:
- A CSV of invoice details saved to reports/
- A printed summary (count, total amount, breakdown by status and vendor)

Usage:
    uv run february_invoices_report.py                        # prompts for dates
    uv run february_invoices_report.py 2026-02-01 2026-03-01  # explicit range
"""

import csv
import sys
from collections import defaultdict
from datetime import datetime

from folio_client import get_client


def parse_date(prompt: str) -> str:
    """Prompt the user for a date until a valid YYYY-MM-DD is entered."""
    while True:
        raw = input(prompt).strip()
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("  Invalid date. Please use YYYY-MM-DD format.")


def get_date_range() -> tuple[str, str]:
    """Return (start_date, end_date) from CLI args or interactive prompts."""
    if len(sys.argv) == 3:
        start, end = sys.argv[1], sys.argv[2]
        # Validate
        for val in (start, end):
            datetime.strptime(val, "%Y-%m-%d")
        return start, end
    print("Enter the invoice date range (YYYY-MM-DD):")
    start = parse_date("  Start date (inclusive): ")
    end = parse_date("  End date   (exclusive):  ")
    return start, end


def run_report(start_date: str, end_date: str) -> None:
    """Fetch invoices in [start_date, end_date) and write a summary report."""
    fc = get_client()
    cql_query = f'invoiceDate>="{start_date}" AND invoiceDate<"{end_date}"'
    print(f"\nFetching invoices from {start_date} to {end_date} (exclusive)...")

    invoices = list(fc.folio_get_all("/invoice/invoices", "invoices", query=cql_query))
    print(f"Found {len(invoices)} invoices.")

    if not invoices:
        print("No invoices found for the specified date range.")
        return

    # --- Write CSV ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"reports/invoices_{start_date}_to_{end_date}_{timestamp}.csv"
    fieldnames = [
        "id",
        "vendorInvoiceNo",
        "invoiceDate",
        "vendorId",
        "status",
        "total",
        "currency",
        "paymentDue",
        "note",
    ]
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for inv in invoices:
            writer.writerow({k: inv.get(k, "") for k in fieldnames})
    print(f"CSV saved to: {output_file}")

    # --- Summary stats ---
    currency = invoices[0].get("currency", "USD")
    total_amount = sum(float(inv.get("total", 0) or 0) for inv in invoices)

    by_status: dict[str, int] = defaultdict(int)
    by_status_amount: dict[str, float] = defaultdict(float)
    by_vendor: dict[str, float] = defaultdict(float)

    for inv in invoices:
        status = inv.get("status", "Unknown")
        vendor = inv.get("vendorId", "Unknown")
        amount = float(inv.get("total", 0) or 0)
        by_status[status] += 1
        by_status_amount[status] += amount
        by_vendor[vendor] += amount

    print(f"\n=== Invoice Summary: {start_date} to {end_date} ===")
    print(f"Total invoices:  {len(invoices)}")
    print(f"Total amount:    {total_amount:,.2f} {currency}")

    print("\nBy status:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count} invoices  ({by_status_amount[status]:,.2f} {currency})")

    print("\nTop vendors by spend:")
    for vendor_id, amount in sorted(by_vendor.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {vendor_id}: {amount:,.2f} {currency}")


def main() -> None:
    """Entry point: resolve date range then run the report."""
    start_date, end_date = get_date_range()
    run_report(start_date, end_date)


if __name__ == "__main__":
    main()
