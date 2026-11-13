"""Regression checks for security-critical configuration.

Lightweight tests: no live database, Redis instance or ML model is required.
"""
import ast
import os
import runpy
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config.py"


def execute_config(secret):
    env = {"SECRET_KEY": secret}
    with patch.dict(os.environ, env, clear=True):
        with patch("dotenv.load_dotenv", return_value=False):
            return runpy.run_path(str(CONFIG))


class SecurityConfigurationTests(unittest.TestCase):
    def test_missing_signing_secret_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "SECRET_KEY"):
            execute_config("")

    def test_short_signing_secret_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "SECRET_KEY"):
            execute_config("short")

    def test_documentation_placeholder_is_not_accepted(self):
        with self.assertRaisesRegex(RuntimeError, "SECRET_KEY"):
            execute_config("replace-with-a-long-random-secret")

    def test_long_signing_secret_is_loaded(self):
        secret = "a" * 48  # test-only dummy, never use for a deployment
        self.assertEqual(execute_config(secret)["SECRET_KEY"], secret)

    def test_database_configuration_uses_environment(self):
        source = (ROOT / "db/database.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        self.assertIn('os.getenv("DATABASE_URL")', source)
        self.assertIn("raise RuntimeError", source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                self.assertNotIn("postgresql://postgres:", node.value)

    def test_migrations_read_environment_connection(self):
        source = (ROOT / "migrations/env.py").read_text(encoding="utf-8")
        self.assertIn("os.getenv('DATABASE_URL')", source)
        self.assertIn("config.set_main_option('sqlalchemy.url'", source)


if __name__ == "__main__":
    unittest.main()
