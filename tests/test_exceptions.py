from turtle_agent.exceptions import (
    AnalysisFailedError,
    ImageTooLargeError,
    InvalidImageError,
    SaveFailedError,
    SpeciesNotFoundError,
    TurtleAgentError,
)


class TestTurtleAgentError:
    def test_base_error_has_code_and_message(self) -> None:
        error = TurtleAgentError(code="TEST_ERROR", message="테스트 에러")
        assert error.code == "TEST_ERROR"
        assert error.message == "테스트 에러"
        assert str(error) == "테스트 에러"

    def test_all_exceptions_inherit_from_base(self) -> None:
        exceptions = [
            InvalidImageError(),
            ImageTooLargeError(size_mb=6.0),
            AnalysisFailedError(),
            SpeciesNotFoundError(species_name="자라"),
            SaveFailedError(),
        ]
        for exc in exceptions:
            assert isinstance(exc, TurtleAgentError)
            assert isinstance(exc, Exception)


class TestInvalidImageError:
    def test_default_message(self) -> None:
        error = InvalidImageError()
        assert error.code == "INVALID_IMAGE"
        assert error.message == "지원하지 않는 이미지 형식입니다"

    def test_custom_message(self) -> None:
        error = InvalidImageError("GIF 형식은 지원하지 않습니다")
        assert error.code == "INVALID_IMAGE"
        assert error.message == "GIF 형식은 지원하지 않습니다"


class TestImageTooLargeError:
    def test_size_in_message(self) -> None:
        error = ImageTooLargeError(size_mb=7.3)
        assert error.code == "IMAGE_TOO_LARGE"
        assert "7.3MB" in error.message
        assert "5.0MB" in error.message

    def test_custom_limit(self) -> None:
        error = ImageTooLargeError(size_mb=12.0, limit_mb=10.0)
        assert "12.0MB" in error.message
        assert "10.0MB" in error.message


class TestAnalysisFailedError:
    def test_default_message(self) -> None:
        error = AnalysisFailedError()
        assert error.code == "ANALYSIS_FAILED"
        assert error.message == "거북이 분석에 실패했습니다"

    def test_custom_message(self) -> None:
        error = AnalysisFailedError("이미지에서 거북이를 찾을 수 없습니다")
        assert error.message == "이미지에서 거북이를 찾을 수 없습니다"


class TestSpeciesNotFoundError:
    def test_species_name_in_message(self) -> None:
        error = SpeciesNotFoundError("자라")
        assert error.code == "SPECIES_NOT_FOUND"
        assert "자라" in error.message


class TestSaveFailedError:
    def test_default_message(self) -> None:
        error = SaveFailedError()
        assert error.code == "SAVE_FAILED"
        assert error.message == "분석 결과 저장에 실패했습니다"
