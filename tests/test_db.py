"""DB layer tests against a throwaway sqlite file — never the real cockpit.db.

db.DB_PATH is swapped for a temp file in setUp and restored in tearDown so
these tests can run in any order, repeatedly, without touching real data.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from app import db


class DbTestCase(unittest.TestCase):
    def setUp(self):
        self._orig_db_path = db.DB_PATH
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        # mkstemp already creates the file; sqlite needs to create its own
        # schema into a fresh file, so remove it and let init_db recreate it.
        os.remove(path)
        db.DB_PATH = Path(path)
        db.init_db()

    def tearDown(self):
        try:
            if db.DB_PATH.exists():
                db.DB_PATH.unlink()
        finally:
            db.DB_PATH = self._orig_db_path


class SessionMessageTests(DbTestCase):
    def test_create_session_add_message_roundtrip(self):
        session_id = db.create_session("ceo", "A")
        self.assertTrue(db.session_exists(session_id))

        db.add_message(session_id, "founder", "A", "hello")
        db.add_message(session_id, "agent", None, "hi there")

        messages = db.list_messages(session_id)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "founder")
        self.assertEqual(messages[0]["founder"], "A")
        self.assertEqual(messages[0]["content"], "hello")
        self.assertEqual(messages[1]["role"], "agent")
        self.assertEqual(messages[1]["content"], "hi there")

    def test_session_exists_false_for_unknown_id(self):
        self.assertFalse(db.session_exists(999999))


class RunTests(DbTestCase):
    def test_create_run_add_log_finish_get_run_roundtrip(self):
        run_id = db.create_run("backend", session_id=None, task="do the thing")
        db.add_run_log(run_id, "tool_call", "Write: some/path.py")
        db.add_run_log(run_id, "warning", "past halfway timeout mark")
        db.finish_run(run_id, "completed")

        run = db.get_run(run_id)
        self.assertIsNotNone(run)
        self.assertEqual(run["agent"], "backend")
        self.assertEqual(run["task"], "do the thing")
        self.assertEqual(run["status"], "completed")
        self.assertIsNotNone(run["ended"])

        event_types = [e["event_type"] for e in run["events"]]
        self.assertEqual(event_types, ["tool_call", "warning"])

    def test_get_run_unknown_id_returns_none(self):
        self.assertIsNone(db.get_run(999999))

    def test_usage_event_cost_surfaces_in_list_runs(self):
        run_id = db.create_run("frontend", session_id=None, task="ship a widget")
        db.add_run_log(
            run_id,
            "usage",
            json.dumps(
                {
                    "input_tokens": 100,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 0,
                    "total_cost_usd": 0.0456,
                }
            ),
        )
        db.finish_run(run_id, "completed")

        runs = {r["id"]: r for r in db.list_runs()}
        self.assertIn(run_id, runs)
        self.assertAlmostEqual(runs[run_id]["cost_usd"], 0.0456, places=6)

    def test_mark_orphaned_runs_closes_running_rows(self):
        run_id_1 = db.create_run("architect", session_id=None, task="task 1")
        run_id_2 = db.create_run("backend", session_id=None, task="task 2")
        db.finish_run(run_id_2, "completed")  # not running any more

        closed = db.mark_orphaned_runs()
        self.assertEqual(closed, 1)

        run_1 = db.get_run(run_id_1)
        self.assertEqual(run_1["status"], "failed")
        self.assertIn("orphaned", run_1["error"])

        run_2 = db.get_run(run_id_2)
        self.assertEqual(run_2["status"], "completed")


if __name__ == "__main__":
    unittest.main()
