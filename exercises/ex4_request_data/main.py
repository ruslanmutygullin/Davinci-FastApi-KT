"""Exercise 4 — request data beyond JSON.

GOAL: implement two endpoints (see test_ex4.py for the exact spec):

  1. POST /contact  — a FORM endpoint taking `name` and `email` form fields, returning
     {"name": ..., "email": ...}.

  2. POST /avatar   — a FILE upload endpoint taking an uploaded `file`, returning
     {"filename": ..., "size": <bytes>}.

Run `pytest -v`, read the failing tests, then complete the TODOs.
Form/file support needs python-multipart (already installed with fastapi[standard]).
"""

from typing import Annotated

from fastapi import FastAPI, Form, File, UploadFile

app = FastAPI()


# TODO 1: implement POST /contact.
#   - Take `name` and `email` as FORM fields (use Annotated[str, Form()]).
#   - Return {"name": name, "email": email}.


# TODO 2: implement POST /avatar.
#   - Take `file` as an uploaded file (Annotated[UploadFile, File()]).
#   - Read its bytes and return {"filename": file.filename, "size": <number of bytes>}.
