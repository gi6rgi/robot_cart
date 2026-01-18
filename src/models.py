from enum import Enum

from pydantic import BaseModel, Field, field_validator


class InvokeRequest(BaseModel):
    journey_notes: list[str] = Field(default_factory=list)
    last_actions: list["Action"] = Field(default_factory=list)
    image_path: str | None = None


class ToolName(str, Enum):
    MOVE_FORWARD = "move_forward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    GO_BACKWARD = "go_backward"


class Action(BaseModel):
    tool: ToolName
    duration: int | None = None

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value, info):
        tool = info.data.get("tool")
        if tool in {ToolName.MOVE_FORWARD, ToolName.GO_BACKWARD}:
            if value is None or value <= 0:
                raise ValueError("duration must be a positive integer for movement tools")
        else:
            if value is not None:
                raise ValueError("duration is only allowed for movement tools")
        return value


class LLMResponse(BaseModel):
    thoughts: str | None = None
    current_journey_note: str
    next_actions: list[Action]


SYSTEM_PROMPT = (
    "You are controlling a robot cart. Use structured JSON output that matches "
    "the LLMResponse schema. Available tools: move_forward(duration seconds), "
    "turn_left(), turn_right(), go_backward(duration seconds). "
    "If journey_notes and last_actions are empty - you are at the beginning of the journey. "
    "Start from looking around to find something interesting. "
    "1 second of moving forward is 20cm of distance. "
    "You will receive a new photo after executing all actions. "
    "Photo is taken from the front of the cart using lens with horizontal FoV ≈ 62.2 degrees. "
    "Choose 1-3 actions per turn. After executing all actions, a new photo "
    "will be captured and provided in the next call.\n\n"
    "Return JSON only."
)
