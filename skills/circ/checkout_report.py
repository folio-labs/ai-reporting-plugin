"""Generate a CSV report of checkout events within a date range.

Columns: title, timestamp, service_point, main_subject

Usage:
    uv run checkout_report.py [--days N]

    Defaults to --days 4 (past four days).

Requires:
    - reports/ directory is created automatically
"""

import argparse
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

from folio_client import get_client

load_dotenv()

REPORTS_DIR = Path("reports")
PAGE_SIZE = 500


# ---------------------------------------------------------------------------
# FOLIO data fetching
# ---------------------------------------------------------------------------


def fetch_checkout_logs(fc, since: datetime) -> list[dict]:
    """Fetch all checkout log entries on or after `since` from the audit log.

    Args:
        fc: Authenticated FolioClient instance.
        since: UTC datetime representing the earliest checkout to include.

    Returns:
        List of log record dicts.
    """
    cutoff = since.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    query = f'action=="Checked out" and date>="{cutoff}"'
    return list(
        fc.folio_get_all(
            "/audit-data/circulation/logs",
            key="logRecords",
            query=query,
            limit=PAGE_SIZE,
        )
    )


def fetch_instances_by_ids(fc, instance_ids: set[str]) -> dict[str, dict]:
    """Fetch inventory instance records for a set of UUIDs.

    Args:
        fc: Authenticated FolioClient instance.
        instance_ids: Set of instance UUIDs to retrieve.

    Returns:
        Mapping of instanceId -> instance record dict.
    """
    if not instance_ids:
        return {}

    cql = "id==(" + " or ".join(f'"{uid}"' for uid in instance_ids) + ")"
    records = fc.folio_get(
        "/inventory/instances",
        key="instances",
        query_params={"query": cql, "limit": len(instance_ids)},
    )
    return {r["id"]: r for r in (records or [])}


def fetch_service_points_by_ids(fc, sp_ids: set[str]) -> dict[str, str]:
    """Fetch service point names for a set of UUIDs.

    Args:
        fc: Authenticated FolioClient instance.
        sp_ids: Set of service point UUIDs to retrieve.

    Returns:
        Mapping of servicePointId -> service point name.
    """
    if not sp_ids:
        return {}

    cql = "id==(" + " or ".join(f'"{uid}"' for uid in sp_ids) + ")"
    records = fc.folio_get(
        "/service-points",
        key="servicepoints",
        query_params={"query": cql, "limit": len(sp_ids)},
    )
    return {r["id"]: r.get("name", r["id"]) for r in (records or [])}


# ---------------------------------------------------------------------------
# Report assembly and CSV output
# ---------------------------------------------------------------------------


def build_report_rows(
    logs: list[dict],
    instances: dict[str, dict],
    service_points: dict[str, str],
    subjects: dict[str, str],
) -> list[dict]:
    """Assemble the final report rows from all fetched data.

    Args:
        logs: Circulation log records.
        instances: Mapping of instanceId -> instance record.
        service_points: Mapping of servicePointId -> name.
        subjects: Mapping of instanceId -> classified subject.

    Returns:
        List of row dicts ready for CSV output.
    """
    rows = []
    for log in logs:
        items = log.get("items") or []
        instance_id = items[0].get("instanceId") if items else None
        instance = instances.get(instance_id, {}) if instance_id else {}

        rows.append(
            {
                "title": instance.get("title", "Unknown"),
                "timestamp": log.get("date", ""),
                "service_point": service_points.get(
                    log.get("servicePointId", ""), "Unknown"
                ),
                "main_subject": (
                    subjects.get(instance_id, "Unclassified")
                    if instance_id
                    else "Unclassified"
                ),
            }
        )
    return rows


def write_csv(rows: list[dict], output_path: Path) -> None:
    """Write report rows to a CSV file.

    Args:
        rows: List of row dicts with keys: title, timestamp, service_point,
            main_subject.
        output_path: Destination path for the CSV file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["title", "timestamp", "service_point", "main_subject"]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the checkout report pipeline."""
    parser = argparse.ArgumentParser(description="Report checkouts from the past N days.")
    parser.add_argument("--days", type=int, default=4, help="Number of days to look back (default: 4)")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=args.days)
    print(f"Fetching checkouts since {since.date()} (past {args.days} days)...")

    fc = get_client()

    logs = fetch_checkout_logs(fc, since)
    print(f"  Retrieved {len(logs)} log entries.")

    # Collect unique IDs for batch lookups
    instance_ids: set[str] = set()
    sp_ids: set[str] = set()
    for log in logs:
        items = log.get("items") or []
        if items and items[0].get("instanceId"):
            instance_ids.add(items[0]["instanceId"])
        if log.get("servicePointId"):
            sp_ids.add(log["servicePointId"])

    print(f"Fetching {len(instance_ids)} unique inventory instances...")
    instances = fetch_instances_by_ids(fc, instance_ids)

    print(f"Fetching {len(sp_ids)} unique service points...")
    service_points = fetch_service_points_by_ids(fc, sp_ids)

    subjects = {}
    for iid, inst in instances.items():
        subj_list = inst.get("subjects")
        if subj_list:
            first = subj_list[0]
            subjects[iid] = first["value"] if isinstance(first, dict) else first

    rows = build_report_rows(logs, instances, service_points, subjects)

    timestamp = now.strftime("%Y%m%d_%H%M%S")
    output_path = REPORTS_DIR / f"checkouts_last{args.days}days_{timestamp}.csv"
    write_csv(rows, output_path)

    print(f"Report written: {output_path}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
