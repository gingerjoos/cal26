"""Manual SQL migration runner for Cal26."""

from __future__ import annotations

import argparse
import logging
import sqlite3
from pathlib import Path
from typing import List, Sequence, Tuple

from .db import Database

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = PROJECT_ROOT / "migrations"


def _ensure_schema_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def _load_applied(conn: sqlite3.Connection) -> set[str]:
    _ensure_schema_table(conn)
    cursor = conn.execute("SELECT version FROM schema_migrations ORDER BY version;")
    return {row[0] for row in cursor.fetchall()}


def _migration_files() -> List[Path]:
    if not MIGRATIONS_DIR.exists():
        raise FileNotFoundError(f"Migrations directory missing: {MIGRATIONS_DIR}")
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def apply_migrations(db: Database, target: str | None = None) -> List[str]:
    """Apply pending migrations up to target (inclusive)."""
    applied_versions: List[str] = []
    files = _migration_files()
    with db.connect() as conn:
        applied = _load_applied(conn)
        for path in files:
            version = path.stem
            if version in applied:
                if target and version == target:
                    break
                continue
            LOGGER.info("Applying migration %s", version)
            script = path.read_text()
            conn.executescript(script)
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)",
                (version,),
            )
            applied_versions.append(version)
            if target and version == target:
                break
    return applied_versions


def list_status(db: Database) -> List[Tuple[str, bool]]:
    """Return all migrations with applied status."""
    files = _migration_files()
    with db.connect() as conn:
        applied = _load_applied(conn)
    return [(path.stem, path.stem in applied) for path in files]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SQLite migration runner")
    parser.add_argument(
        "--database",
        help="Override database path (defaults to SQLITE_PATH or cal26.db)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    apply_parser = subparsers.add_parser("apply", help="Apply pending migrations")
    apply_parser.add_argument(
        "--target",
        help="Apply up to and including the specified migration version",
    )

    subparsers.add_parser("show", help="Display migration status")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for the migration runner CLI."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = _build_parser()
    args = parser.parse_args(argv)
    db = Database(path=args.database)

    if args.command == "apply":
        applied = apply_migrations(db, target=args.target)
        if applied:
            LOGGER.info("Applied migrations: %s", ", ".join(applied))
        else:
            LOGGER.info("No migrations to apply")
    elif args.command == "show":
        for version, done in list_status(db):
            status = "✓" if done else "·"
            print(f"{status} {version}")
    else:
        parser.error("Unknown command")


if __name__ == "__main__":
    main()
