"""Isolated database runtime checks; do not connect to production services."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def launch(source, url):
    env = os.environ.copy()
    env["DATABASE_URL"] = url
    env["PYTHON_DOTENV_DISABLED"] = "1"
    return subprocess.run(
        [sys.executable, "-c", source],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


class DatabaseRuntimeTests(unittest.TestCase):
    def test_sqlalchemy_session_executes_sqlite_query(self):
        result = launch(
            "from sqlalchemy import text\n"
            "from db.database import engine, SessionLocal\n"
            "with engine.connect() as conn:\n"
            "    assert conn.execute(text('SELECT 1')).scalar_one() == 1\n"
            "with SessionLocal() as session:\n"
            "    assert session.execute(text('SELECT 2')).scalar_one() == 2\n",
            "sqlite+pysqlite:///:memory:",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_empty_database_url_fails_closed(self):
        result = launch("import db.database\n", "")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DATABASE_URL is required", result.stderr)


if __name__ == "__main__":
    unittest.main()
