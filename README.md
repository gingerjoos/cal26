
# Cal26

Minimal Starlette + SQLite backend for managing Swetha’s 2026 calendar orders.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (preferred) or `pip`
- SQLite (bundled with Python)

## Install dependencies

```bash
uv sync
```

This creates `.venv/` with all dependencies defined in `pyproject.toml`.

## Running the development server

1. Copy `.env.example` to `.env` and fill the required values (admin creds, paths, etc.).
1. Ensure the database is initialized (see next section).
1. Start the ASGI server:

```bash
uv run uvicorn cal26.app:create_app --reload
```

The app listens on `http://127.0.0.1:8000/` by default.

## Initializing the database

1. Apply migrations (creates `cal26.db` unless `SQLITE_PATH` is set):

```bash
uv run python -m cal26.migrate apply
```

1. Seed the initial admin user from environment variables:

```bash
uv run python -m cal26.seed_admin
```

- Reads `ADMIN_BASIC_AUTH_USER`, `ADMIN_BASIC_AUTH_PASS`, and the first address listed in `ADMIN_NOTIFICATION_EMAILS`.

1. To inspect migration status:

```bash
uv run python -m cal26.migrate show
```

## Helpful environment variables

- `SQLITE_PATH`: absolute path to the SQLite file (defaults to `cal26.db` in repo root)
- `ADMIN_BASIC_AUTH_USER`, `ADMIN_BASIC_AUTH_PASS`: dashboard credentials
- `ADMIN_NOTIFICATION_EMAILS`: comma-separated list; first entry seeds the admin account

See `.env.example` for the full list used across the app.
