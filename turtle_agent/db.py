import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path("turtle_analysis.db")


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """SQLite 커넥션을 반환한다."""
    return sqlite3.connect(str(db_path))


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    """분석 이력 테이블이 없으면 생성한다."""
    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id TEXT PRIMARY KEY,
                species TEXT NOT NULL,
                species_confidence REAL NOT NULL,
                gender TEXT NOT NULL,
                gender_confidence REAL NOT NULL,
                distinguishing_features TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
