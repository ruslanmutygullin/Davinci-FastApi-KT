from sqlmodel import SQLModel, Field


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = False
