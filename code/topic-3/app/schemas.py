from sqlmodel import SQLModel


class NoteCreate(SQLModel):
    title: str
    done: bool = False


class NoteRead(SQLModel):
    id: int
    title: str
    done: bool
