from enum import Enum

from pydantic import BaseModel, field_validator


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


DEFAULT_PRIORITY = Priority.MEDIUM

# Sort weight for `GET /tasks?sort=priority`: high first, low last.
# Keyed by the plain string values held in TaskStorage.
PRIORITY_ORDER: dict[str, int] = {
    Priority.HIGH.value: 0,
    Priority.MEDIUM.value: 1,
    Priority.LOW.value: 2,
}


def clean_title(value: str) -> str:
    """Normalise a title, rejecting blank input. Whitespace-only counts as empty."""
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("title must not be empty")
    return cleaned


class TaskCreate(BaseModel):
    title: str
    priority: Priority = DEFAULT_PRIORITY

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return clean_title(value)


class TaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None
    priority: Priority | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        # `None` means "field omitted, leave it alone" rather than "set to empty".
        if value is None:
            return None
        return clean_title(value)


class Task(BaseModel):
    id: int
    title: str
    completed: bool
    priority: Priority
