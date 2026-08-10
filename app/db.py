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


def create_run(agent: str, session_id: int | None, task: str) -> int:
    conn = _connect()
    try:
        cur = conn.execute(
            "INSERT INTO runs (agent, session_id, task, status, started) "
            "VALUES (?, ?, ?, ?, ?)",
            (agent, session_id, task, "running", _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def finish_run(run_id: int, status: str, error: str | None = None) -> None:
    conn = _connect()
    try:
        conn.execute(
            "UPDATE runs SET status = ?, ended = ?, error = ? WHERE id = ?",
            (status, _now(), error, run_id),
        )
        conn.commit()
    finally:
        conn.close()


def add_run_log(run_id: int, event_type: str, detail: str) -> None:
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO run_log (run_id, event_type, detail, timestamp) "
            "VALUES (?, ?, ?, ?)",
            (run_id, event_type, detail, _now()),
        )
        conn.commit()
    finally:
        conn.close()


def list_runs(limit: int = 100) -> list[dict]:
    conn = _connect()
    try:
        rows = conn.execute(
            """
            SELECT r.id, r.agent, r.session_id,
                   substr(r.task, 1, 120) AS task,
                   r.status, r.started, r.ended, r.error,
                   (SELECT SUM(json_extract(l.detail, '$.total_cost_usd'))
                    FROM run_log l
                    WHERE l.run_id = r.id AND l.event_type = 'usage') AS cost_usd
            FROM runs r
            ORDER BY r.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        columns = [
            "id", "agent", "session_id", "task",
            "status", "started", "ended", "error", "cost_usd",
        ]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()


def get_run(run_id: int) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT id, agent, session_id, task, status, started, ended, error "
            "FROM runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        columns = ["id", "agent", "session_id", "task", "status", "started", "ended", "error"]
        run = dict(zip(columns, row))

        events = conn.execute(
            "SELECT event_type, detail, timestamp FROM run_log "
            "WHERE run_id = ? ORDER BY id ASC",
            (run_id,),
        ).fetchall()
        run["events"] = [
            {"event_type": e[0], "detail": e[1], "timestamp": e[2]} for e in events
        ]
        return run
    finally:
        conn.close()
