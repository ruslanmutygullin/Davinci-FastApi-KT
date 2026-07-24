"""A domain exception, decoupled from HTTP. main.py registers a handler that maps it
to a 404 response — so business logic can raise it without knowing about status codes.
"""


class NoteNotFoundError(Exception):
    def __init__(self, note_id: int):
        self.note_id = note_id
