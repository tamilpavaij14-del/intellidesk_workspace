import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

DEFAULT_MODEL = os.environ.get("LLM_MODEL", "gemini-3.5-flash-lite")
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def complete(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    retries: int = 2
) -> str:

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

            return response.text

        except Exception as e:
            last_error = e

            if attempt < retries:
                time.sleep(2 ** attempt)

    raise RuntimeError(
        f"LLM request failed after {retries + 1} attempts: {last_error}"
    )


def stream(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE
):
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