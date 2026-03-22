import pytest
from pydantic import ValidationError

from turtle_agent.models import (
    ApiResponse,
    ErrorDetail,
    TurtleAnalysisResult,
    TurtleGender,
    TurtleSpecies,
)

VALID_RESULT_DATA = {
    "species": TurtleSpecies.RED_EARED_SLIDER,
    "species_confidence": 0.85,
    "gender": TurtleGender.MALE,
    "gender_confidence": 0.72,
    "distinguishing_features": ["귀 뒤 붉은 반점", "올리브색 등갑"],
    "description": "붉은귀거북 수컷으로 판별됩니다.",
}


class TestTurtleAnalysisResultValid:
    def test_valid_result(self) -> None:
        result = TurtleAnalysisResult(**VALID_RESULT_DATA)
        assert result.species == TurtleSpecies.RED_EARED_SLIDER
        assert result.gender == TurtleGender.MALE
        assert result.species_confidence == 0.85
        assert result.gender_confidence == 0.72
        assert len(result.distinguishing_features) == 2

    def test_all_species(self) -> None:
        for species in TurtleSpecies:
            result = TurtleAnalysisResult(**{**VALID_RESULT_DATA, "species": species})
            assert result.species == species

    def test_all_genders(self) -> None:
        for gender in TurtleGender:
            result = TurtleAnalysisResult(**{**VALID_RESULT_DATA, "gender": gender})
            assert result.gender == gender

    def test_whitespace_stripped(self) -> None:
        result = TurtleAnalysisResult(**{**VALID_RESULT_DATA, "description": "  앞뒤 공백  "})
        assert result.description == "앞뒤 공백"


class TestConfidenceBoundary:
    def test_species_confidence_zero(self) -> None:
        result = TurtleAnalysisResult(**{**VALID_RESULT_DATA, "species_confidence": 0.0})
        assert result.species_confidence == 0.0

    def test_species_confidence_one(self) -> None:
        result = TurtleAnalysisResult(**{**VALID_RESULT_DATA, "species_confidence": 1.0})
        assert result.species_confidence == 1.0

    def test_gender_confidence_zero(self) -> None:
        result = TurtleAnalysisResult(**{**VALID_RESULT_DATA, "gender_confidence": 0.0})
        assert result.gender_confidence == 0.0

    def test_gender_confidence_one(self) -> None:
        result = TurtleAnalysisResult(**{**VALID_RESULT_DATA, "gender_confidence": 1.0})
        assert result.gender_confidence == 1.0

    def test_species_confidence_mid(self) -> None:
        result = TurtleAnalysisResult(**{**VALID_RESULT_DATA, "species_confidence": 0.5})
        assert result.species_confidence == 0.5


class TestConfidenceInvalid:
    def test_species_confidence_negative(self) -> None:
        with pytest.raises(ValidationError, match="species_confidence"):
            TurtleAnalysisResult(**{**VALID_RESULT_DATA, "species_confidence": -0.1})

    def test_species_confidence_over_one(self) -> None:
        with pytest.raises(ValidationError, match="species_confidence"):
            TurtleAnalysisResult(**{**VALID_RESULT_DATA, "species_confidence": 1.1})

    def test_gender_confidence_negative(self) -> None:
        with pytest.raises(ValidationError, match="gender_confidence"):
            TurtleAnalysisResult(**{**VALID_RESULT_DATA, "gender_confidence": -0.01})

    def test_gender_confidence_over_one(self) -> None:
        with pytest.raises(ValidationError, match="gender_confidence"):
            TurtleAnalysisResult(**{**VALID_RESULT_DATA, "gender_confidence": 1.5})


class TestInvalidInput:
    def test_invalid_species(self) -> None:
        with pytest.raises(ValidationError, match="species"):
            TurtleAnalysisResult(**{**VALID_RESULT_DATA, "species": "자라"})

    def test_invalid_gender(self) -> None:
        with pytest.raises(ValidationError, match="gender"):
            TurtleAnalysisResult(**{**VALID_RESULT_DATA, "gender": "모름"})

    def test_missing_required_field(self) -> None:
        incomplete = {k: v for k, v in VALID_RESULT_DATA.items() if k != "species"}
        with pytest.raises(ValidationError, match="species"):
            TurtleAnalysisResult(**incomplete)

    def test_confidence_not_a_number(self) -> None:
        with pytest.raises(ValidationError, match="species_confidence"):
            TurtleAnalysisResult(**{**VALID_RESULT_DATA, "species_confidence": "높음"})

    def test_empty_features_allowed(self) -> None:
        result = TurtleAnalysisResult(**{**VALID_RESULT_DATA, "distinguishing_features": []})
        assert result.distinguishing_features == []


class TestApiResponse:
    def test_success_response(self) -> None:
        analysis = TurtleAnalysisResult(**VALID_RESULT_DATA)
        response = ApiResponse[TurtleAnalysisResult](success=True, data=analysis)
        assert response.success is True
        assert response.data is not None
        assert response.data.species == TurtleSpecies.RED_EARED_SLIDER
        assert response.error is None

    def test_error_response(self) -> None:
        error = ErrorDetail(code="INVALID_IMAGE", message="지원하지 않는 이미지 형식입니다")
        response = ApiResponse[TurtleAnalysisResult](success=False, error=error)
        assert response.success is False
        assert response.data is None
        assert response.error.code == "INVALID_IMAGE"
