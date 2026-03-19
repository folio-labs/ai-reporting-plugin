"""FOLIO API client factory.

Loads credentials from a .env file and returns an authenticated FolioClient.
"""

import os

from dotenv import load_dotenv
from folioclient import FolioClient


def get_client() -> FolioClient:
    """Create and return an authenticated FolioClient using .env credentials.

    Returns:
        An authenticated FolioClient instance.

    Raises:
        EnvironmentError: If any required environment variable is missing.
    """
    load_dotenv()

    required = ("FOLIO_URL", "FOLIO_TENANT", "FOLIO_USERNAME", "FOLIO_PASSWORD")
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in your FOLIO credentials."
        )

    return FolioClient(
        os.environ["FOLIO_URL"],
        os.environ["FOLIO_TENANT"],
        os.environ["FOLIO_USERNAME"],
        os.environ["FOLIO_PASSWORD"],
    )
