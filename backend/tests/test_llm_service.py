from src.models.roadmap import CareerRoadmap
from src.services.llm_service import _gemini_json_schema


def test_gemini_schema_removes_pydantic_numeric_constraints() -> None:
    schema = _gemini_json_schema(CareerRoadmap)

    assert "exclusiveMinimum" not in str(schema)
    assert "exclusiveMaximum" not in str(schema)
