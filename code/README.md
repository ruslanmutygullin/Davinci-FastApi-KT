# Runnable Code Companion

Working code for the [FastAPI for JS Developers](../docs/README.md) docs. Each `topic-N/`
folder is a snapshot of the **same Notes API** as it grows across the three topics — clone
it, run it, break it, read the tests.

- `topic-1/` — single file, in-memory. Routes, Pydantic, CRUD, auto docs.
- `topic-2/` — structured `app/` package with SQLModel database and dependency injection.
- `topic-3/` — production concerns: config, JWT auth, CORS, tests, Docker.

Want practice instead of reading? See [`../exercises/`](../exercises/README.md).

## Setup (once)

You need **Python 3.11+** (the code is written against 3.14). From this `code/` folder:

```bash
# create and activate a virtual environment
python -m venv .venv
source .venv/Scripts/activate     # Windows Git Bash
# .venv\Scripts\activate          # Windows PowerShell/CMD
# source .venv/bin/activate       # macOS / Linux

# install everything the three stages need
pip install -r requirements.txt
```

## Run a stage

```bash
# Topic 1 — single file
cd topic-1
uvicorn main:app --reload

# Topic 2 & 3 — package layout
cd topic-2   # or topic-3
uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000/docs** for the interactive API.

## Run the tests

Each stage ships with passing reference tests so you can see the expected behavior:

```bash
cd topic-1 && pytest -v      # or topic-2, topic-3
```

## Notes

- **SQLite is used everywhere** so there's zero setup — the database is a local file
  (`notes.db`) created on first run. Topic 3 includes a `Dockerfile` and a
  `docker-compose.yml` showing the Postgres swap, but you do **not** need Docker or Postgres
  to run or test any stage.
- Topic 3 reads config from environment variables / a `.env` file. Copy `.env.example` to
  `.env` to customize; sensible defaults work out of the box.
