class TurtleAgentError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class InvalidImageError(TurtleAgentError):
    def __init__(self, message: str = "지원하지 않는 이미지 형식입니다") -> None:
        super().__init__(code="INVALID_IMAGE", message=message)


class ImageTooLargeError(TurtleAgentError):
    def __init__(self, size_mb: float, limit_mb: float = 5.0) -> None:
        super().__init__(
            code="IMAGE_TOO_LARGE",
            message=f"이미지 크기({size_mb:.1f}MB)가 제한({limit_mb:.1f}MB)을 초과합니다",
        )


class AnalysisFailedError(TurtleAgentError):
    def __init__(self, message: str = "거북이 분석에 실패했습니다") -> None:
        super().__init__(code="ANALYSIS_FAILED", message=message)


class SpeciesNotFoundError(TurtleAgentError):
    def __init__(self, species_name: str) -> None:
        super().__init__(
            code="SPECIES_NOT_FOUND",
            message=f"도감에서 '{species_name}' 종을 찾을 수 없습니다",
        )


class SaveFailedError(TurtleAgentError):
    def __init__(self, message: str = "분석 결과 저장에 실패했습니다") -> None:
        super().__init__(code="SAVE_FAILED", message=message)
