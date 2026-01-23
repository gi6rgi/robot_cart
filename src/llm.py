from google import genai

from src.config import settings
from src.models import SYSTEM_PROMPT, InvokeRequest, LLMResponse

client = genai.Client(api_key=settings.gemini.api_key)


def build_prompt(request: InvokeRequest) -> str:
    parts = [SYSTEM_PROMPT]
    if request.journey_notes:
        notes = "\n".join(f"- {note}" for note in request.journey_notes)
        parts.append(f"Journey notes:\n{notes}")
    if request.last_actions:
        actions = ", ".join(action.tool for action in request.last_actions)
        parts.append(f"Last actions: {actions}")
    return "\n\n".join(parts)


def invoke(request: InvokeRequest) -> LLMResponse:
    contents = [build_prompt(request)]
    print(f"LLM Invokation:\n\n{contents}")

    if request.image_path:
        with open(request.image_path, "rb") as image:
            contents.append(image.read())

    response = client.models.generate_content(
        model=settings.gemini.model,
        contents=contents,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": LLMResponse.model_json_schema(),
        },
    )

    response = LLMResponse.model_validate_json(response.text)
    return response
