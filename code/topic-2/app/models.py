"""The database table. `table=True` makes this a real SQL table, not just a schema."""

from sqlmodel import SQLModel, Field


class Note(SQLModel, table=True):
    # id is assigned by the DB on insert, so it's optional before the row exists.
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = False
