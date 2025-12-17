"""SQLite helper utilities for Cal26."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "cal26.db"


def resolve_database_path(path: str | Path | None = None) -> Path:
    """Resolve the SQLite database path."""
    if path:
        return Path(path).expanduser()
    env_path = os.getenv("SQLITE_PATH")
    if env_path:
        return Path(env_path).expanduser()
    return DEFAULT_DB_PATH


class Database:
    """Lightweight SQLite helper offering parameterized query helpers."""

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = resolve_database_path(path)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Yield a SQLite connection with sensible defaults."""
        conn = sqlite3.connect(self._path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def execute(self, query: str, params: Sequence[Any] | None = None) -> None:
        """Execute a write query."""
        with self.connect() as conn:
            conn.execute(query, params or [])

    def executemany(
        self,
        query: str,
        param_batches: Iterable[Sequence[Any]],
    ) -> None:
        """Execute a parameterized query for multiple batches."""
        with self.connect() as conn:
            conn.executemany(query, list(param_batches))

    def fetch_one(
        self,
        query: str,
        params: Sequence[Any] | None = None,
    ) -> sqlite3.Row | None:
        """Return a single row for the given query."""
        with self.connect() as conn:
            cursor = conn.execute(query, params or [])
            return cursor.fetchone()

    def fetch_all(
        self,
        query: str,
        params: Sequence[Any] | None = None,
    ) -> list[sqlite3.Row]:
        """Return all rows matching the query."""
        with self.connect() as conn:
            cursor = conn.execute(query, params or [])
            return cursor.fetchall()

    def execute_script(self, script: str) -> None:
        """Execute a multi-statement SQL script."""
        with self.connect() as conn:
            conn.executescript(script)
