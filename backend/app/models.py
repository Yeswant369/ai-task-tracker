from pydantic import BaseModel, field_validator


def clean_title(value: str) -> str:
    """Normalise a title, rejecting blank input. Whitespace-only counts as empty."""
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("title must not be empty")
    return cleaned


class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return clean_title(value)


class TaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None

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
