"""Entry point for SUL AI FOLIO Reporting.

Run this script to verify your FOLIO credentials and connection:

    uv run main.py
"""

from folio_client import get_client


def main() -> None:
    """Verify FOLIO connection and print basic tenant info."""
    fc = get_client()
    print(f"Connected to FOLIO: {fc.okapi_url} (tenant: {fc.tenant_id})")


if __name__ == "__main__":
    main()
