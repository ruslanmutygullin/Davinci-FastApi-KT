"""Topic 1 — request data beyond the JSON body.

Not every request is JSON. This demo shows the other places data comes from and how each
is still just a typed parameter:
  - form fields (Form)
  - file uploads (UploadFile)
  - typed headers (Header) and cookies (Cookie)

Run it:   uvicorn request_data:app --reload
Tests:    pytest test_request_data.py -v

Note: form/file support needs `python-multipart`, which ships with fastapi[standard].
"""

from typing import Annotated

from fastapi import FastAPI, Form, File, UploadFile, Header, Cookie

app = FastAPI(title="Topic 1 — Request Data")


@app.post("/login")
async def login(
    # Form fields come from an application/x-www-form-urlencoded body, NOT JSON.
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    return {"user": username, "password_len": len(password)}


@app.post("/upload")
async def upload(file: Annotated[UploadFile, File()]):
    # UploadFile streams to a spooled temp file — good for large uploads.
    contents = await file.read()
    return {"filename": file.filename, "content_type": file.content_type, "size": len(contents)}


@app.get("/whoami")
async def whoami(
    # A typed header. FastAPI maps `user_agent` <-> the `User-Agent` header automatically.
    user_agent: Annotated[str | None, Header()] = None,
    # A cookie read straight off the request.
    session_id: Annotated[str | None, Cookie()] = None,
):
    return {"user_agent": user_agent, "session_id": session_id}
