"""Composition root for Topic 3: adds CORS and a centralized exception handler.

Run it:  uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.errors import NoteNotFoundError
from app.routers import notes


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

# CORS: allow the configured frontend origin(s). Without this, browsers block the response.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes.router)


@app.exception_handler(NoteNotFoundError)
async def note_not_found_handler(_request: Request, exc: NoteNotFoundError):
    # One place that turns a domain error into an HTTP response.
    return JSONResponse(
        status_code=404,
        content={"error": f"Note {exc.note_id} does not exist"},
    )
