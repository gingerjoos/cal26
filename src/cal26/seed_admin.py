"""Seed the initial admin user from environment variables."""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
from typing import Sequence
from uuid import uuid4

from dotenv import load_dotenv

from .db import Database

load_dotenv()

LOGGER = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Return a deterministic hash for the given password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _env_or_raise(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set before seeding admin user")
    return value


def _resolve_admin_email() -> str:
    raw = os.getenv("ADMIN_NOTIFICATION_EMAILS", "")
    primary = next((email.strip() for email in raw.split(",") if email.strip()), "")
    if not primary:
        raise RuntimeError(
            "ADMIN_NOTIFICATION_EMAILS must contain at least one email to seed admin"
        )
    return primary


def seed_admin_user(db: Database) -> str:
    """Insert or update the primary admin user."""
    username = _env_or_raise("ADMIN_BASIC_AUTH_USER")
    password = _env_or_raise("ADMIN_BASIC_AUTH_PASS")
    email = _resolve_admin_email()
    display_name = os.getenv("ADMIN_NAME", username)

    password_hash = hash_password(password)

    row = db.fetch_one("SELECT id FROM users WHERE email = ?", (email,))
    if row:
        db.execute(
            """
            UPDATE users
            SET name = ?, password_hash = ?, is_staff = 1, updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
            """,
            (display_name, password_hash, email),
        )
        LOGGER.info("Updated existing admin user (%s)", email)
        return row["id"]

    user_id = str(uuid4())
    db.execute(
        """
        INSERT INTO users (id, name, email, password_hash, is_staff)
        VALUES (?, ?, ?, ?, 1)
        """,
        (user_id, display_name, email, password_hash),
    )
    LOGGER.info("Created admin user (%s)", email)
    return user_id


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entrypoint for the admin seeding helper."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="Seed admin user from env vars")
    parser.add_argument(
        "--database",
        help="Optional path to SQLite database (defaults to SQLITE_PATH or cal26.db)",
    )
    args = parser.parse_args(argv)

    db = Database(path=args.database)
    seed_admin_user(db)


if __name__ == "__main__":
    main()
