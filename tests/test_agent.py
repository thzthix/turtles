import pytest
from pydantic_ai.models.test import TestModel

from turtle_agent.agent import SYSTEM_PROMPT, create_agent, analyze_turtle_image
from turtle_agent.models import TurtleAnalysisResult, TurtleGender, TurtleSpecies

FAKE_IMAGE_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00"


@pytest.fixture
def test_agent():
    return create_agent(model=TestModel(call_tools=[]))


class TestAgentStructure:
    def test_output_type_is_turtle_analysis_result(self, test_agent) -> None:
        assert test_agent.output_type is TurtleAnalysisResult

    def test_tools_registered(self, test_agent) -> None:
        tool_names = {name for name in test_agent._function_toolset.tools}
        assert "lookup_species" in tool_names
        assert "save_analysis" in tool_names

    def test_tool_count(self, test_agent) -> None:
        assert len(test_agent._function_toolset.tools) == 2

    def test_instructions_not_empty(self) -> None:
        assert SYSTEM_PROMPT
        assert "판별" in SYSTEM_PROMPT


class TestAnalyzeTurtleImage:
    @pytest.mark.anyio
    async def test_returns_turtle_analysis_result(self, test_agent) -> None:
        result = await analyze_turtle_image(FAKE_IMAGE_BYTES, "image/png", agent=test_agent)
        assert isinstance(result, TurtleAnalysisResult)

    @pytest.mark.anyio
    async def test_result_has_valid_species(self, test_agent) -> None:
        result = await analyze_turtle_image(FAKE_IMAGE_BYTES, "image/png", agent=test_agent)
        assert result.species in TurtleSpecies

    @pytest.mark.anyio
    async def test_result_has_valid_gender(self, test_agent) -> None:
        result = await analyze_turtle_image(FAKE_IMAGE_BYTES, "image/png", agent=test_agent)
        assert result.gender in TurtleGender

    @pytest.mark.anyio
    async def test_result_confidence_in_range(self, test_agent) -> None:
        result = await analyze_turtle_image(FAKE_IMAGE_BYTES, "image/png", agent=test_agent)
        assert 0.0 <= result.species_confidence <= 1.0
        assert 0.0 <= result.gender_confidence <= 1.0

    @pytest.mark.anyio
    async def test_result_has_features_and_description(self, test_agent) -> None:
        result = await analyze_turtle_image(FAKE_IMAGE_BYTES, "image/png", agent=test_agent)
        assert isinstance(result.distinguishing_features, list)
        assert isinstance(result.description, str)
