from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TurtleSpecies(StrEnum):
    RED_EARED_SLIDER = "붉은귀거북"
    PENINSULA_COOTER = "페닌슐라쿠터"
    JEWELED_TURTLE = "보석거북"
    YELLOW_BELLIED_SLIDER = "옐로우밸리"
    PINK_BELLIED_SIDE_NECK = "핑크밸리"


class TurtleGender(StrEnum):
    MALE = "수컷"
    FEMALE = "암컷"
    UNCERTAIN = "불확실"


class TurtleAnalysisResult(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    species: TurtleSpecies = Field(description="판별된 거북이 종류")
    species_confidence: float = Field(ge=0.0, le=1.0, description="종 판별 확신도 (0.0 ~ 1.0)")
    gender: TurtleGender = Field(description="판별된 성별")
    gender_confidence: float = Field(ge=0.0, le=1.0, description="성별 판별 확신도 (0.0 ~ 1.0)")
    distinguishing_features: list[str] = Field(description="판별 근거가 된 외형 특징 목록")
    description: str = Field(description="종합 분석 설명")


class ErrorDetail(BaseModel):
    code: str = Field(description="에러 코드")
    message: str = Field(description="에러 메시지")


class ApiResponse[T](BaseModel):
    success: bool = Field(description="요청 성공 여부")
    data: T | None = Field(default=None, description="응답 데이터")
    error: ErrorDetail | None = Field(default=None, description="에러 상세")
