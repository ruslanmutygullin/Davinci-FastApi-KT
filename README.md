# FastAPI for JavaScript Developers

A hands-on course that teaches Node/JS developers how to **create and maintain** FastAPI
projects from scratch. Python basics are assumed; every concept is anchored to something
you already know from Express / Nest / Prisma.

The course is three parts working together:

- **[`docs/`](./docs/README.md)** — the theory. How FastAPI works and *why*, with Node
  analogies throughout.
- **[`code/`](./code/README.md)** — runnable apps you can clone, run, and break. One
  **Notes API** grows across three topics.
- **[`exercises/`](./exercises/README.md)** — guided practice: failing tests you make pass,
  with solutions to check against.

Start with [`docs/README.md`](./docs/README.md).

## What's covered

| Topic | Docs | Runnable code | Focus |
|-------|------|---------------|-------|
| 1 | [session-1.md](./docs/session-1.md) | [code/topic-1](./code/topic-1/) | Request lifecycle, ASGI, Pydantic validation, `Annotated`, request data, serialization, OpenAPI |
| 2 | [session-2.md](./docs/session-2.md) | [code/topic-2](./code/topic-2/) | Project structure, SQLModel database, dependency injection |
| 3 | [session-3.md](./docs/session-3.md) | [code/topic-3](./code/topic-3/) | Config, errors, testing, CORS, JWT auth, Docker, async |

Plus a [glossary](./docs/glossary.md) mapping every term (ASGI, coercion, session, event
loop, …) to a Node equivalent.

## Setup

Requires **Python 3.11+** (written against 3.14).

```bash
# from the project root
python -m venv .venv
source .venv/Scripts/activate     # Windows Git Bash
# .venv\Scripts\activate          # Windows PowerShell/CMD
# source .venv/bin/activate       # macOS / Linux

pip install -r code/requirements.txt
```

## Run an app

```bash
cd code/topic-1
uvicorn main:app --reload          # topic-1 is a single file

cd code/topic-2                     # topic-2 & 3 use a package layout
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** for the interactive API.

## Run the tests

Each topic and exercise is a self-contained app, so run tests from inside its folder:

```bash
cd code/topic-1 && pytest      # topic-1: 20 tests
cd code/topic-2 && pytest      # topic-2:  5 tests
cd code/topic-3 && pytest      # topic-3:  7 tests
```

All reference tests pass (32 total). Exercise **solutions** pass (11 total); the exercise
**stubs** are meant to fail until you complete them — that's the point.

## Repository layout

```
.
├── docs/          # theory (session-1..3, glossary, README)
├── code/          # runnable apps (topic-1..3) + requirements.txt
├── exercises/     # practice stubs + solutions/
├── pyproject.toml
└── .gitignore
```
