"""Path-guard matrix tests: allow/deny for each assigned agent plus the CEO.

Guards are built exactly the way run_assigned_task / _ceo_options build
them (same config accessors, same kwargs) so these tests exercise the real
wiring, not a re-implementation of it. No API calls, no server, no network
— make_path_guard's returned callback only resolves paths and compares them
against config data.
"""

import asyncio
import unittest

from app import agents, config

ALLOW = "PermissionResultAllow"
DENY = "PermissionResultDeny"


def check(guard, tool_name: str, path: str) -> str:
    """Run the guard for one tool call and return the result type name."""
    result = asyncio.run(guard(tool_name, {"file_path": path}, None))
    return type(result).__name__


class BackendGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = agents.make_path_guard(
            config.agent_write_paths("backend"),
            deny_paths=config.agent_deny_paths("backend"),
        )

    def test_write_backend_app_allowed(self):
        self.assertEqual(
            check(self.guard, "Write", r"C:\loop-labs\carwash-app\backend\app\main.py"),
            ALLOW,
        )

    def test_write_backend_migrations_allowed(self):
        self.assertEqual(
            check(
                self.guard,
                "Write",
                r"C:\loop-labs\carwash-app\backend\migrations\001_init.py",
            ),
            ALLOW,
        )

    def test_write_integrations_carveout_denied(self):
        self.assertEqual(
            check(
                self.guard,
                "Write",
                r"C:\loop-labs\carwash-app\backend\app\integrations\payments.py",
            ),
            DENY,
        )

    def test_edit_integrations_carveout_denied(self):
        self.assertEqual(
            check(
                self.guard,
                "Edit",
                r"C:\loop-labs\carwash-app\backend\app\integrations\payments.py",
            ),
            DENY,
        )

    def test_write_client_denied(self):
        self.assertEqual(
            check(self.guard, "Write", r"C:\loop-labs\carwash-app\client\lib\main.dart"),
            DENY,
        )

    def test_write_cockpit_app_denied(self):
        self.assertEqual(
            check(self.guard, "Write", r"C:\loop-labs\loop-labs-cockpit\app\main.py"),
            DENY,
        )

    def test_write_own_playbook_allowed(self):
        self.assertEqual(
            check(
                self.guard,
                "Write",
                str(config.COMPANY_DIR / "agents" / "backend" / "playbook.md"),
            ),
            ALLOW,
        )

    def test_write_own_report_allowed(self):
        self.assertEqual(
            check(
                self.guard,
                "Write",
                str(config.REPORTS_DIR / "2026-08-11-backend-run99.md"),
            ),
            ALLOW,
        )

    def test_read_env_file_denied(self):
        # Never open this file — the guard only receives its path string.
        self.assertEqual(check(self.guard, "Read", str(config.ENV_FILE)), DENY)

    def test_read_client_allowed(self):
        # Reads range over the whole allowed-roots set, not just write_paths.
        self.assertEqual(
            check(self.guard, "Read", r"C:\loop-labs\carwash-app\client\lib\main.dart"),
            ALLOW,
        )


class FrontendGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = agents.make_path_guard(
            config.agent_write_paths("frontend"),
            deny_paths=config.agent_deny_paths("frontend"),
        )

    def test_write_client_allowed(self):
        self.assertEqual(
            check(self.guard, "Write", r"C:\loop-labs\carwash-app\client\lib\main.dart"),
            ALLOW,
        )

    def test_write_backend_denied(self):
        self.assertEqual(
            check(self.guard, "Write", r"C:\loop-labs\carwash-app\backend\app\main.py"),
            DENY,
        )

    def test_write_design_denied(self):
        self.assertEqual(
            check(self.guard, "Write", r"C:\loop-labs\carwash-app\design\theme.dart"),
            DENY,
        )


class ArchitectGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = agents.make_path_guard(
            config.agent_write_paths("architect"),
            deny_paths=config.agent_deny_paths("architect"),
        )

    def test_write_ownership_map_allowed(self):
        self.assertEqual(
            check(self.guard, "Write", str(config.COMPANY_DIR / "ownership.md")),
            ALLOW,
        )

    def test_write_contracts_allowed(self):
        self.assertEqual(
            check(
                self.guard,
                "Write",
                r"C:\loop-labs\carwash-app\contracts\openapi.yaml",
            ),
            ALLOW,
        )

    def test_write_docs_allowed(self):
        self.assertEqual(
            check(self.guard, "Write", r"C:\loop-labs\carwash-app\docs\adr\001.md"),
            ALLOW,
        )

    def test_write_backend_denied(self):
        self.assertEqual(
            check(self.guard, "Write", r"C:\loop-labs\carwash-app\backend\x.py"),
            DENY,
        )

    def test_edit_own_playbook_allowed(self):
        self.assertEqual(
            check(
                self.guard,
                "Edit",
                str(config.COMPANY_DIR / "agents" / "architect" / "playbook.md"),
            ),
            ALLOW,
        )


class CeoGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = agents.make_path_guard(
            config.CEO_WRITE_PATHS,
            allow_tool_prefixes=("mcp__cockpit__",),
            write_globs=config.CEO_WRITE_GLOBS,
        )

    def test_assign_task_tool_allowed(self):
        self.assertEqual(
            check(self.guard, "mcp__cockpit__assign_task", "unused"),
            ALLOW,
        )

    def test_write_architect_brief_allowed(self):
        self.assertEqual(
            check(
                self.guard,
                "Write",
                str(config.COMPANY_DIR / "agents" / "architect" / "brief.md"),
            ),
            ALLOW,
        )

    def test_write_architect_playbook_denied(self):
        self.assertEqual(
            check(
                self.guard,
                "Write",
                str(config.COMPANY_DIR / "agents" / "architect" / "playbook.md"),
            ),
            DENY,
        )

    def test_write_app_main_denied(self):
        self.assertEqual(
            check(self.guard, "Write", str(config.REPO_ROOT / "app" / "main.py")),
            DENY,
        )


if __name__ == "__main__":
    unittest.main()
