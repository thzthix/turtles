import json
import sqlite3
from pathlib import Path

import pytest

from turtle_agent.exceptions import SpeciesNotFoundError
from turtle_agent.tools import load_species_data, lookup_species, save_analysis


class TestLoadSpeciesData:
    def test_returns_dict_with_five_species(self) -> None:
        data = load_species_data()
        assert isinstance(data, dict)
        assert len(data) == 5

    def test_contains_all_species(self) -> None:
        data = load_species_data()
        expected = {"붉은귀거북", "페닌슐라쿠터", "보석거북", "옐로우밸리", "핑크밸리"}
        assert set(data.keys()) == expected


class TestLookupSpecies:
    def test_valid_species(self) -> None:
        result = lookup_species("붉은귀거북")
        assert result["scientific_name"] == "Trachemys scripta elegans"
        assert "appearance" in result
        assert "gender_traits" in result

    def test_all_species_have_required_fields(self) -> None:
        required_fields = {"scientific_name", "common_name_en", "habitat", "lifespan_years", "appearance", "gender_traits"}
        for species_name in load_species_data():
            result = lookup_species(species_name)
            assert required_fields.issubset(result.keys()), f"{species_name}에 필수 필드 누락"

    def test_unknown_species_raises(self) -> None:
        with pytest.raises(SpeciesNotFoundError, match="자라"):
            lookup_species("자라")


class TestSaveAnalysis:
    VALID_PARAMS = {
        "species": "붉은귀거북",
        "species_confidence": 0.92,
        "gender": "수컷",
        "gender_confidence": 0.78,
        "distinguishing_features": ["귀 뒤 붉은 반점", "긴 앞발 발톱"],
        "description": "붉은귀거북 수컷으로 판별",
    }

    def test_returns_id(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        analysis_id = save_analysis(**self.VALID_PARAMS, db_path=db_path)
        assert isinstance(analysis_id, str)
        assert len(analysis_id) == 12

    def test_data_persisted(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        analysis_id = save_analysis(**self.VALID_PARAMS, db_path=db_path)
        conn = sqlite3.connect(str(db_path))
        row = conn.execute("SELECT * FROM analysis_history WHERE id = ?", (analysis_id,)).fetchone()
        conn.close()
        assert row is not None
        assert row[1] == "붉은귀거북"
        assert row[3] == "수컷"

    def test_features_stored_as_json(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        analysis_id = save_analysis(**self.VALID_PARAMS, db_path=db_path)
        conn = sqlite3.connect(str(db_path))
        row = conn.execute("SELECT distinguishing_features FROM analysis_history WHERE id = ?", (analysis_id,)).fetchone()
        conn.close()
        features = json.loads(row[0])
        assert features == ["귀 뒤 붉은 반점", "긴 앞발 발톱"]

    def test_multiple_saves_unique_ids(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        id1 = save_analysis(**self.VALID_PARAMS, db_path=db_path)
        id2 = save_analysis(**self.VALID_PARAMS, db_path=db_path)
        assert id1 != id2
