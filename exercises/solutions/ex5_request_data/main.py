"""Exercise 5 — SOLUTION."""

from typing import Annotated

from fastapi import FastAPI, Form, File, UploadFile

app = FastAPI()


@app.post("/contact")
async def contact(
    name: Annotated[str, Form()],
    email: Annotated[str, Form()],
):
    return {"name": name, "email": email}


@app.post("/avatar")
async def avatar(file: Annotated[UploadFile, File()]):
    data = await file.read()
    return {"filename": file.filename, "size": len(data)}
