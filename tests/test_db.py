import sqlite3
from pathlib import Path

from turtle_agent.db import get_connection, init_db


class TestGetConnection:
    def test_returns_connection(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        conn = get_connection(db_path)
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_creates_db_file(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        conn = get_connection(db_path)
        conn.close()
        assert db_path.exists()


class TestInitDb:
    def test_creates_table(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        init_db(db_path)
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_history'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_idempotent(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        init_db(db_path)
        init_db(db_path)
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='analysis_history'")
        assert cursor.fetchone()[0] == 1
        conn.close()
