from pathlib import Path

from pydantic_ai import Agent, BinaryContent, Tool

from turtle_agent.models import TurtleAnalysisResult
from turtle_agent.tools import lookup_species, save_analysis

MODEL = "anthropic:claude-sonnet-4-5"

SYSTEM_PROMPT = """
TODO: 시스템 프롬프트를 함께 다듬을 예정.
아래는 placeholder이며, 최종 프롬프트는 CLAUDE.md의 '시스템 프롬프트 설계 방향'에 따라 작성한다.

당신은 거북이 종류와 성별을 판별하는 전문가입니다.
""".strip()

turtle_agent = Agent(
    MODEL,
    output_type=TurtleAnalysisResult,
    instructions=SYSTEM_PROMPT,
    tools=[
        Tool(lookup_species, description="거북이 도감에서 종 상세 정보를 조회한다"),
        Tool(save_analysis, description="분석 결과를 DB에 저장하고 저장 ID를 반환한다"),
    ],
)


async def analyze_turtle_image(image_data: bytes, media_type: str) -> TurtleAnalysisResult:
    """거북이 이미지를 분석하여 종류와 성별을 판별한다."""
    result = await turtle_agent.run(
        [
            "이 거북이의 종류와 성별을 판별해주세요.",
            BinaryContent(data=image_data, media_type=media_type),
        ],
    )
    return result.output
