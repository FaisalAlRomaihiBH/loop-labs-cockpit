"""Config/company sanity checks: briefs exist, models resolve, the secrets
file is never inside a path an agent can read or write, static context
files are present, and the kill switch is not tripped.
"""

import unittest

from app import config

ASSIGNABLE_AGENTS = ("ceo", "architect", "backend", "frontend")


class AgentSanityTests(unittest.TestCase):
    def test_every_agent_has_a_brief(self):
        for name in ASSIGNABLE_AGENTS:
            brief = config.AGENTS_DIR / name / "brief.md"
            self.assertTrue(brief.exists(), f"missing brief for {name}: {brief}")

    def test_every_agent_resolves_a_model(self):
        for name in ASSIGNABLE_AGENTS:
            model = config.MODELS.get(name, config.MODELS["default"])
            self.assertTrue(model, f"no model resolved for {name}")
            self.assertIsInstance(model, str)


class EnvFileIsolationTests(unittest.TestCase):
    def test_env_file_not_under_allowed_paths(self):
        for root in config.ALLOWED_PATHS:
            self.assertFalse(
                config.ENV_FILE == root or config.ENV_FILE.is_relative_to(root),
                f"ENV_FILE must not be under allowed root {root}",
            )

    def test_env_file_not_under_any_agent_write_paths(self):
        for name in ASSIGNABLE_AGENTS:
            if name == "ceo":
                write_paths = config.CEO_WRITE_PATHS
            else:
                write_paths = config.agent_write_paths(name)
            for path in write_paths:
                self.assertFalse(
                    config.ENV_FILE == path or config.ENV_FILE.is_relative_to(path),
                    f"ENV_FILE must not be under {name}'s write path {path}",
                )


class ContextDocsTests(unittest.TestCase):
    def test_ceo_static_and_volatile_docs_exist(self):
        for path in config.CEO_STATIC_DOCS:
            self.assertTrue(path.exists(), f"missing static doc: {path}")
        for path, _heading in config.CEO_VOLATILE_DOCS:
            self.assertTrue(path.exists(), f"missing volatile doc: {path}")


class KillSwitchTests(unittest.TestCase):
    def test_kill_file_does_not_exist(self):
        self.assertFalse(config.KILL_FILE.exists())


if __name__ == "__main__":
    unittest.main()
