import json
import sqlite3
import uuid
from pathlib import Path

from turtle_agent.exceptions import SaveFailedError, SpeciesNotFoundError

SPECIES_DATA_PATH = Path(__file__).parent / "data" / "species.json"
DEFAULT_DB_PATH = Path("turtle_analysis.db")


def load_species_data() -> dict:
    with SPECIES_DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def lookup_species(species_name: str) -> dict:
    """거북이 도감에서 종 상세 정보를 조회한다."""
    data = load_species_data()
    if species_name not in data:
        raise SpeciesNotFoundError(species_name)
    return data[species_name]


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    """분석 이력 테이블이 없으면 생성한다."""
    conn = sqlite3.connect(str(db_path))
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


def save_analysis(
    species: str,
    species_confidence: float,
    gender: str,
    gender_confidence: float,
    distinguishing_features: list[str],
    description: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    """분석 결과를 SQLite에 저장하고 저장 ID를 반환한다."""
    init_db(db_path)
    analysis_id = uuid.uuid4().hex[:12]
    try:
        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute(
                """
                INSERT INTO analysis_history
                    (id, species, species_confidence, gender, gender_confidence, distinguishing_features, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    species,
                    species_confidence,
                    gender,
                    gender_confidence,
                    json.dumps(distinguishing_features, ensure_ascii=False),
                    description,
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        raise SaveFailedError(str(e)) from e
    return analysis_id
