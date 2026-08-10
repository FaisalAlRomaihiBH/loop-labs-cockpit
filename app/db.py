"""SQLite persistence layer for the cockpit plumbing milestone.

Stdlib sqlite3 only, connection-per-call so it's safe to use from async
request handlers (no shared connection/cursor state across awaits).
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "cockpit.db"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                founder TEXT,
                started TEXT NOT NULL,
                ended TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL REFERENCES sessions(id),
                role TEXT NOT NULL,
                founder TEXT,
                content TEXT NOT NULL,
                created TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                session_id INTEGER REFERENCES sessions(id),
                task TEXT,
                status TEXT NOT NULL,
                started TEXT NOT NULL,
                ended TEXT,
                error TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS run_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL REFERENCES runs(id),
                event_type TEXT NOT NULL,
                detail TEXT,
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def create_session(agent: str, founder: str | None) -> int:
    conn = _connect()
    try:
        cur = conn.execute(
            "INSERT INTO sessions (agent, founder, started) VALUES (?, ?, ?)",
            (agent, founder, _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def add_message(session_id: int, role: str, founder: str | None, content: str) -> int:
    conn = _connect()
    try:
        cur = conn.execute(
            "INSERT INTO messages (session_id, role, founder, content, created) "
            "VALUES (?, ?, ?, ?, ?)",
            (session_id, role, founder, content, _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def session_exists(session_id: int) -> bool:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        return row is not None
    finally:
        conn.close()
