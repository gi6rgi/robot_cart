import mimetypes
import time

from google import genai
from google.genai import types

from src.config import settings
from src.models import SYSTEM_PROMPT, InvokeRequest, LLMResponse

RETRIES = 10
client = genai.Client(api_key=settings.gemini.api_key)


def build_prompt(request: InvokeRequest) -> str:
    parts = [SYSTEM_PROMPT]
    if request.goal:
        parts.append(f"\nGoal: {request.goal}\n")
    if request.journey_notes:
        notes = "\n".join(f"- {note}" for note in request.journey_notes)
        parts.append(f"Journey notes:\n{notes}")
    if request.last_actions:
        actions = ", ".join(action.tool for action in request.last_actions)
        parts.append(f"Last actions: {actions}")
    return "\n\n".join(parts)


def _build_contents(request: InvokeRequest) -> list[str | types.Part]:
    contents: list[str | types.Part] = [build_prompt(request)]
    if request.image_path:
        mime_type, _ = mimetypes.guess_type(request.image_path)
        if mime_type is None:
            mime_type = "image/png"
        with open(request.image_path, "rb") as image:
            contents.append(types.Part.from_bytes(data=image.read(), mime_type=mime_type))
    return contents


def _generate_response(contents: list[str | types.Part]) -> LLMResponse:
    response = client.models.generate_content(
        model=settings.gemini.model,
        contents=contents,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": LLMResponse.model_json_schema(),
        },
    )
    return LLMResponse.model_validate_json(response.text)


def invoke(request: InvokeRequest) -> LLMResponse:
    last_error: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            contents = _build_contents(request)
            print(f"LLM Invokation:\n\n{contents}")
            return _generate_response(contents)
        except Exception as exc:
            last_error = exc
            if attempt == RETRIES:
                break
            delay = min(0.5 * (2 ** (attempt - 1)), 8.0)
            print(
                "LLM invoke failed "
                f"(attempt {attempt}/{RETRIES}): {exc}. Retrying in {delay:.2f}s"
            )
            time.sleep(delay)
    raise last_error if last_error is not None else RuntimeError("LLM invoke failed")
