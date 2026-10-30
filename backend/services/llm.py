import json
import os
import re
import time
from typing import Any

from dotenv import load_dotenv
from google import genai

load_dotenv()

DEFAULT_MODEL = os.environ.get("LLM_MODEL", "gemini-3.5-flash-lite")
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024

# Initialize the Gemini client using your API key.
_api_key = os.environ.get("GEMINI_API_KEY")

if not _api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add it to your local backend/.env file."
    )

_client = genai.Client(api_key=_api_key)


def complete(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    retries: int = 2,
) -> str:
    """Generate a complete response using the Gemini API."""

    last_error = None

    for attempt in range(retries + 1):
        try:
            response = _client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": DEFAULT_MAX_TOKENS,
                },
            )

            return response.text or ""

        except Exception as exc:
            last_error = exc

            if attempt < retries:
                time.sleep(2**attempt)

    raise RuntimeError(
        f"LLM request failed after {retries + 1} attempts: {last_error}"
    ) from last_error


def extract_json(response: str) -> dict[str, Any]:
    """Extract and parse a JSON object from an LLM response."""

    if not isinstance(response, str) or not response.strip():
        raise ValueError("The LLM response is empty.")

    # First, try parsing the complete response.
    try:
        parsed = json.loads(response)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # Remove common Markdown JSON code fences.
    cleaned = re.sub(
        r"^\s*```(?:json)?\s*|\s*```\s*$",
        "",
        response.strip(),
        flags=re.IGNORECASE,
    )

    # Try parsing the cleaned response.
    try:
        parsed = json.loads(cleaned)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # Find a JSON object embedded in surrounding text.
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end > start:
        try:
            parsed = json.loads(cleaned[start : end + 1])

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError as exc:
            raise ValueError(
                "The response does not contain valid JSON."
            ) from exc

    raise ValueError("No valid JSON object was found in the response.")


def stream(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
):
    """Stream a response from the Gemini API in chunks."""

    response = _client.models.generate_content_stream(
        model=model,
        contents=prompt,
        config={
            "temperature": temperature,
            "max_output_tokens": DEFAULT_MAX_TOKENS,
        },
    )

    for chunk in response:
        if chunk.text:
            yield chunk.text
