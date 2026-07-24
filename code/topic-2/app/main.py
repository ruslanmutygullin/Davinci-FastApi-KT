"""Composition root: create the FastAPI app, run startup, mount routers.

Run it:  uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import notes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Everything before `yield` runs once at startup; after `yield`, at shutdown.
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(notes.router)
