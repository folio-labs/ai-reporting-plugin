# SUL AI FOLIO Reporting

AI-assisted circulation reporting for library staff using the FOLIO library services platform.

Library staff use an AI coding assistant (Claude Code, Google Gemini CLI, or OpenAI Codex) to 
generate custom circulation and inventory reports by querying FOLIO APIs.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package and project manager
- Python 3.12+
- Access to a FOLIO instance (URL, tenant, username, password)

## Setup

1. **Install dependencies**

   ```bash
   uv sync
   ```

2. **Configure credentials**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your FOLIO credentials:

   ```
   FOLIO_URL=https://your-folio-instance.example.edu
   FOLIO_TENANT=your_tenant_id
   FOLIO_USERNAME=your_username
   FOLIO_PASSWORD=your_password
   ```

3. **Verify your connection**

   ```bash
   uv run main.py
   ```

   A successful connection prints your FOLIO URL and tenant ID.

## Using with an AI Agent

Open this repository in your preferred AI coding assistant and describe the report you want. Example prompts:

- *"Show me all items checked out in the past 30 days by location."*
- *"List overdue loans grouped by patron group."*
- *"Export a CSV of active holds for the Main Library."*

The assistant will query the FOLIO Inventory and Circulation APIs using the `FolioClient` in `folio_client.py`.

## Project Structure

```
.
├── folio_client.py   # Authenticated FolioClient factory (reads .env)
├── main.py           # Connection verification script
├── pyproject.toml    # Project metadata and dependencies (managed by uv)
├── .env.example      # Credential template — copy to .env
└── AGENTS.md         # AI agent instructions and project mandates
```

## Key APIs

All requests go through `FolioClient`. Common endpoints:

| Area        | Endpoint                              |
|-------------|---------------------------------------|
| Items       | `/inventory/items`                    |
| Instances   | `/inventory/instances`                |
| Loans       | `/circulation/loans`                  |
| Requests    | `/circulation/requests`               |
| Loan policies | `/loan-policy-storage/loan-policies`|

Use CQL (Contextual Query Language) for filtering, e.g.:
```
status.name=="Checked out" and effectiveLocation.name=="Main Library"
```

## Development

```bash
uv run ruff check .    # Lint
uv run ruff format .   # Format
uv run pytest          # Run tests
```
