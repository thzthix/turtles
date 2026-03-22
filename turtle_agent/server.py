from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from turtle_agent.agent import analyze_turtle_image, create_agent
from turtle_agent.exceptions import TurtleAgentError
from turtle_agent.models import ApiResponse, ErrorDetail, TurtleAnalysisResult

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/webp"}

app = FastAPI(title="Turtle Analyzer Agent", version="0.1.0")
_agent = None


def get_agent():
    """에이전트를 lazy 초기화하여 반환한다."""
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent


@app.exception_handler(TurtleAgentError)
async def turtle_agent_error_handler(request, exc: TurtleAgentError) -> JSONResponse:
    """커스텀 예외를 ApiResponse 에러 형식으로 변환한다."""
    return JSONResponse(
        status_code=400,
        content=ApiResponse[None](
            success=False,
            error=ErrorDetail(code=exc.code, message=exc.message),
        ).model_dump(),
    )


def validate_media_type(content_type: str | None) -> str:
    """업로드된 파일의 미디어 타입을 검증하고 반환한다."""
    if content_type not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(
            status_code=400,
            detail=ApiResponse[None](
                success=False,
                error=ErrorDetail(
                    code="INVALID_IMAGE",
                    message=f"지원하지 않는 이미지 형식입니다. 허용: {', '.join(ALLOWED_MEDIA_TYPES)}",
                ),
            ).model_dump(),
        )
    return content_type


def validate_image_size(size: int) -> None:
    """이미지 크기를 검증한다."""
    if size > MAX_IMAGE_SIZE_BYTES:
        size_mb = size / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=ApiResponse[None](
                success=False,
                error=ErrorDetail(
                    code="IMAGE_TOO_LARGE",
                    message=f"이미지 크기({size_mb:.1f}MB)가 제한(5.0MB)을 초과합니다",
                ),
            ).model_dump(),
        )


@app.post("/analyze", response_model=ApiResponse[TurtleAnalysisResult])
async def analyze(file: UploadFile) -> ApiResponse[TurtleAnalysisResult]:
    """거북이 이미지를 분석하여 종류와 성별을 판별한다."""
    media_type = validate_media_type(file.content_type)
    image_data = await file.read()
    validate_image_size(len(image_data))
    result = await analyze_turtle_image(image_data, media_type, agent=get_agent())
    return ApiResponse[TurtleAnalysisResult](success=True, data=result)
