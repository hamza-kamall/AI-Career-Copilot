"""LLM provider helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

TModel = TypeVar("TModel", bound=BaseModel)


def is_gemini_enabled() -> bool:
    """Return whether Gemini should be used for generation."""
    return os.getenv("LLM_PROVIDER", "mock").strip().lower() == "gemini" and bool(
        _api_key()
    )


def generate_structured(prompt: str, schema: type[TModel]) -> TModel:
    """Generate a Pydantic model from Gemini structured output."""
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError("google-genai is not installed") from exc

    client = genai.Client(api_key=_api_key())
    response = client.models.generate_content(
        model=os.getenv("LLM_MODEL", "gemini-3.5-flash"),
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=_gemini_json_schema(schema),
        ),
    )

    if getattr(response, "parsed", None) is not None:
        return schema.model_validate(response.parsed)
    if not response.text:
        raise RuntimeError("Gemini returned an empty response")
    return schema.model_validate_json(response.text)


def _api_key() -> str:
    return os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY", "")


def _gemini_json_schema(schema: type[TModel]) -> dict[str, object]:
    """Return a Gemini-compatible JSON schema for a Pydantic model."""
    return _strip_unsupported_schema_keys(schema.model_json_schema())


def _strip_unsupported_schema_keys(value: object) -> object:
    unsupported_keys = {
        "exclusiveMinimum",
        "exclusiveMaximum",
        "minimum",
        "maximum",
        "multipleOf",
    }
    if isinstance(value, dict):
        return {
            key: _strip_unsupported_schema_keys(item)
            for key, item in value.items()
            if key not in unsupported_keys
        }
    if isinstance(value, list):
        return [_strip_unsupported_schema_keys(item) for item in value]
    return value
