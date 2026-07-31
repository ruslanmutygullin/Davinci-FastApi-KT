"""API contract schemas, separate from the table model (models.py).

Pydantic v2 validators enforce business rules here — invalid data is rejected
before it reaches the service layer.
"""

from pydantic import ConfigDict, field_validator, model_validator
from sqlmodel import SQLModel


class NoteCreate(SQLModel):
    title: str
    done: bool = False

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v.strip()


class NoteUpdate(SQLModel):
    """Partial update — every field is optional; client sends only what changes.

    extra="forbid" rejects unknown fields so a typo like "titl" surfaces as a 422
    rather than silently doing nothing. Combined with model_dump(exclude_unset=True)
    in the service, omitted fields are left untouched.
    """

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    done: bool | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("title must not be blank")
        return v.strip() if v else v

    @model_validator(mode="after")
    def at_least_one_field(self) -> "NoteUpdate":
        if self.title is None and self.done is None:
            raise ValueError("provide at least one field to update")
        return self


class NoteRead(SQLModel):
    id: int
    title: str
    done: bool
    owner: str | None = None
