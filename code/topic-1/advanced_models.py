"""Topic 1 — richer Pydantic modeling, as a runnable demo.

Shows three things beyond the basic Notes API:
  1. Field constraints + a str Enum (validation richer than just the type)
  2. Nested models and lists, plus optional-vs-required rules
  3. Custom validators (@field_validator, @model_validator) for rules types can't express

Run it:   uvicorn advanced_models:app --reload
Docs at:  http://127.0.0.1:8000/docs   (see the constraints/enum/examples render)
Tests:    pytest test_advanced_models.py -v
"""

from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator, model_validator

app = FastAPI(title="Topic 1 — Advanced Models")


# --- 1. Constraints + Enum -------------------------------------------------

class Priority(str, Enum):
    """A str Enum: FastAPI validates input to one of these and shows a dropdown in docs."""

    low = "low"
    medium = "medium"
    high = "high"


class Tag(BaseModel):
    # Field(...) adds constraints beyond the type + docs metadata (description/examples).
    name: str = Field(min_length=1, max_length=20, examples=["work"])


# --- 2. Nested models, lists, optional-vs-required -------------------------

class TaskCreate(BaseModel):
    # Required: no default -> the client MUST send it.
    title: str = Field(min_length=1, max_length=200)

    # Optional with a real default value.
    priority: Priority = Priority.medium

    # Optional and may be explicitly null: `| None` + default None.
    due_days: int | None = Field(default=None, ge=0, le=365)

    # A list of NESTED models — validation recurses into each Tag.
    tags: list[Tag] = []

    # --- 3. Custom validators ---------------------------------------------

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        # Runs after type validation; normalize + enforce a rule types can't express.
        v = v.strip()
        if not v:
            raise ValueError("title must not be blank")
        return v

    @model_validator(mode="after")
    def high_priority_needs_due_date(self):
        # Cross-field rule: a high-priority task must have a due date.
        if self.priority is Priority.high and self.due_days is None:
            raise ValueError("high-priority tasks require due_days")
        return self


@app.post("/tasks")
async def create_task(task: TaskCreate):
    # By the time we're here, `task` is fully validated and normalized.
    return task
