# Topic 3 — Production Patterns: Services, Migrations, Validators & Testing

This topic bridges the gap between a working demo and a maintainable production service.
The notes app from Topic 2 gets a service layer, schema validators, Alembic migrations, and
a full test suite. Each addition mirrors a pattern from the real codebase.

> ▶ **Run the code:** [`code/topic-3/`](../code/topic-3/) — Practice:
> [`exercises/ex3_service_and_validators`](../exercises/ex3_service_and_validators/) ·
> [`exercises/ex5_mocking_parametrize`](../exercises/ex5_mocking_parametrize/)

```
app/
├── main.py           # CORS, exception handler, lifespan
├── config.py         # pydantic-settings
├── database.py       # engine + init_db
├── dependencies.py   # SessionDep, CurrentUserDep, require_api_key
├── models.py         # Note table
├── schemas.py        # NoteCreate, NoteUpdate (with validators), NoteRead
├── errors.py         # NoteNotFoundError
├── auth.py           # JWT: get_current_user, create_access_token
├── services/
│   └── notes.py      # NoteService — all business logic lives here
└── routers/
    └── notes.py      # thin HTTP layer — calls service, returns result
alembic/
├── env.py
└── versions/
    ├── 0001_initial.py
    └── 0002_add_owner.py
tests/
├── conftest.py
├── test_notes_router.py   # TestClient — HTTP contract tests
├── test_notes_service.py  # direct service calls — logic tests
└── test_schemas.py        # parametrize — validator tests
```

---

## 1. Configuration as validated data

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./notes.db"
    api_key: str = "secret123"
    jwt_secret: str = "change-me-in-production-this-is-only-a-demo-secret"
    cors_origins: list[str] = ["http://localhost:5173"]
    webhook_url: str = ""

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

When `Settings()` constructs it reads environment variables first (case-insensitive:
`DATABASE_URL` → `database_url`), then `.env`, then field defaults. A field with no default
is **required** — the app refuses to start with a clear error rather than failing
mysteriously at request time.

- Never commit `.env`. Commit `.env.example` with dummy values.
- In production, inject real values as platform env vars — no file needed.
- `cors_origins: list[str]` reads `CORS_ORIGINS=http://a.com,http://b.com` as a list automatically.

---

## 2. The service layer

### Why

The Topic 2 router handled everything: DB queries, validation, error raising. That works
for a tutorial. It becomes a problem when you need the same logic from two endpoints, or
want to test logic without spinning up HTTP, or the function grows complex enough to deserve
its own test file.

The fix is a **service layer** — a plain Python module between the router and the database.

```
routers/notes.py    ← HTTP: params, status codes, response_model
services/notes.py   ← logic: queries, validation, side effects
models / database   ← storage
```

### The service

```python
# app/services/notes.py
import httpx
from sqlmodel import Session, select

from app.config import settings
from app.errors import NoteNotFoundError
from app.models import Note
from app.schemas import NoteCreate, NoteUpdate


def _notify(note: Note) -> None:
    """Best-effort webhook — failures are swallowed, never break the request."""
    if not settings.webhook_url:
        return
    try:
        httpx.post(settings.webhook_url, json={"id": note.id, "title": note.title}, timeout=5)
    except Exception:
        pass


class NoteService:
    def get(self, db: Session, note_id: int) -> Note:
        note = db.get(Note, note_id)
        if not note:
            raise NoteNotFoundError(note_id)   # domain exception, not HTTPException
        return note

    def create(self, db: Session, payload: NoteCreate) -> Note:
        note = Note(title=payload.title, done=payload.done)
        db.add(note)
        db.commit()
        db.refresh(note)
        _notify(note)   # external side effect — easy to mock in tests
        return note

    def patch(self, db: Session, note_id: int, payload: NoteUpdate) -> Note:
        note = self.get(db, note_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(note, key, value)
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    # get_all, update, delete follow the same shape

note_service = NoteService()   # stateless singleton
```

The service has **no FastAPI imports**. It raises `NoteNotFoundError` — a domain exception
that `main.py`'s exception handler converts to HTTP. The service can be called from tests,
CLI scripts, background tasks, or other services without any HTTP machinery.

### The router

```python
# app/routers/notes.py
from app.dependencies import CurrentUserDep, SessionDep, require_api_key
from app.schemas import NoteCreate, NoteRead, NoteUpdate
from app.services.notes import note_service

router = APIRouter(tags=["notes"])


@router.post("/notes", response_model=NoteRead, status_code=201)
async def create_note(payload: NoteCreate, session: SessionDep, current_user: CurrentUserDep):
    return note_service.create(session, payload)


@router.patch("/notes/{note_id}", response_model=NoteRead)
async def patch_note(note_id: int, payload: NoteUpdate, session: SessionDep, current_user: CurrentUserDep):
    return note_service.patch(session, note_id, payload)


@router.delete("/notes/{note_id}", status_code=204, dependencies=[Depends(require_api_key)])
async def delete_note(note_id: int, session: SessionDep):
    note_service.delete(session, note_id)
```

Three lines per handler: declare what you need, call the service, return. No logic.

### Side effects in the service

`_notify()` above is the mocking teaching vehicle, but the pattern is real: UCM's
`services/usecase.py` calls `coveo_service.sync(...)` after every DB commit, wrapped in
`try/except` so a Coveo failure never rolls back a successful DB write. Keeping side effects
in the service (not the router) means they can be mocked without touching HTTP machinery.

---

## 3. Pydantic v2 validators

Pydantic v2 lets you add custom validation logic directly on schemas. This is how both
services enforce business rules — rejected at the schema boundary, before data reaches the
service.

### `@field_validator` — single-field validation and transformation

```python
# app/schemas.py
from pydantic import ConfigDict, field_validator, model_validator
from sqlmodel import SQLModel


class NoteCreate(SQLModel):
    title: str
    done: bool = False

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v.strip()   # return value replaces the field — "  hello  " → "hello"
```

A `ValueError` inside a validator becomes a `422` response with the field name in
`detail[].loc`. The return value **replaces** the input, so validators can transform as
well as reject. Both happen here: blank titles are rejected and valid ones are stripped.

### `extra="forbid"` — reject unknown fields

By default Pydantic ignores extra fields. On an update schema a typo like `"titl"` silently
does nothing. `extra="forbid"` turns it into a 422:

```python
class NoteUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    done: bool | None = None
```

`PATCH /notes/1` with `{"titl": "typo"}` now returns:
```json
{"detail": [{"loc": ["body", "titl"], "msg": "Extra inputs are not permitted"}]}
```

### `@model_validator` — cross-field validation

When the rule spans multiple fields, `@model_validator(mode="after")` runs on the
fully-constructed object:

```python
class NoteUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = None
    done: bool | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "NoteUpdate":
        if self.title is None and self.done is None:
            raise ValueError("provide at least one field to update")
        return self
```

`PATCH /notes/1` with `{}` now returns 422 instead of silently doing nothing.

### `model_dump(exclude_unset=True)`

The PATCH companion — distinguishes "field omitted" from "field set to null":

```python
# in NoteService.patch
for key, value in payload.model_dump(exclude_unset=True).items():
    setattr(note, key, value)
```

`PATCH {"done": true}` updates only `done`. Without `exclude_unset=True` the `None`
default for `title` would overwrite the existing value.

---

## 4. Alembic migrations

### Why `create_all()` is dev-only

`SQLModel.metadata.create_all(engine)` creates tables that don't exist. It **never alters
existing tables**. Add a column to `Note`, restart the app — `create_all` sees the table
exists and skips it. The column is silently absent in production.

**Alembic** is your `prisma migrate` — versioned SQL scripts that apply changes
incrementally and track which ones have run.

### Setup

```bash
pip install alembic
alembic init alembic
```

Configure `alembic/env.py` to read the DB URL from settings and target `SQLModel.metadata`:

```python
# alembic/env.py
from sqlmodel import SQLModel
import app.models   # registers models with SQLModel.metadata

target_metadata = SQLModel.metadata

def get_url() -> str:
    from app.config import settings
    return settings.database_url
```

### The workflow

```bash
# 1. Change your model — e.g. add `owner: str | None = None` to Note
# 2. Generate a migration
alembic revision --autogenerate -m "add owner to note"
# 3. Review alembic/versions/0002_add_owner.py — always check autogenerated output
# 4. Apply
alembic upgrade head
# Roll back one step
alembic downgrade -1
```

The generated file for the `owner` column:

```python
# alembic/versions/0002_add_owner.py
revision: str = "0002"
down_revision: Union[str, None] = "0001"   # linked list of migrations

def upgrade() -> None:
    op.add_column("note", sa.Column("owner", sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column("note", "owner")
```

Each file has a `revision` id and `down_revision` pointer forming a chain. `alembic upgrade
head` walks the chain and applies any unapplied migrations.

> UCM has 17 migration files in `alembic/versions/` — every schema change since the initial
> deploy. `alembic upgrade head` on a fresh database builds the full current schema from
> scratch.

### Testing: keep using `create_all()`

In tests, use `SQLModel.metadata.create_all(engine)` on an in-memory SQLite database.
Migrations are for managing a long-lived production schema; tests throw the database away
after each run.

---

## 5. Querying

`select()` builds a statement object. Nothing hits the database until `session.exec()`:

```python
from sqlmodel import select

stmt = select(Note).order_by(Note.id)
if done is not None:
    stmt = stmt.where(Note.done == done)
if search:
    stmt = stmt.where(Note.title.contains(search))
stmt = stmt.offset((page - 1) * size).limit(size)
return list(db.exec(stmt).all())
```

This is the full `get_all` implementation from `NoteService`. Query parameters `?done=false&search=meeting&page=2` are handled by the router and passed in as typed Python values — FastAPI coerces them automatically.

Common patterns:

```python
# Filtering
select(Note).where(Note.done == True)                       # equality
select(Note).where(Note.title.contains("meeting"))          # LIKE '%meeting%'
select(Note).where(Note.title.ilike("%meeting%"))           # case-insensitive
select(Note).where(Note.done == False, Note.title.startswith("Q"))  # AND

from sqlalchemy import or_
select(Note).where(or_(Note.done == True, Note.title == "urgent"))  # OR

# Ordering
from sqlalchemy import desc
select(Note).order_by(desc(Note.title))

# Counting
from sqlalchemy import func
session.exec(select(func.count()).select_from(Note)).one()
```

> **`==` not `is`** — `Note.done is False` is a Python identity check, always wrong in a
> `.where()`. Use `==`.

| Terminal         | Returns                   | Raises if                 |
|------------------|---------------------------|---------------------------|
| `.all()`         | `list` (empty if no rows) | —                         |
| `.first()`       | first row or `None`       | —                         |
| `.one()`         | exactly one row           | zero or more than one row |
| `.one_or_none()` | one row or `None`         | more than one row         |

`db.get(Note, pk)` is a PK shortcut that checks the session cache before hitting the DB.

---

## 6. Error handling

```python
# app/errors.py
class NoteNotFoundError(Exception):
    def __init__(self, note_id: int):
        self.note_id = note_id
```

```python
# app/main.py
@app.exception_handler(NoteNotFoundError)
async def note_not_found_handler(request: Request, exc: NoteNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": f"Note {exc.note_id} does not exist"},
    )
```

The service raises `NoteNotFoundError` — it knows nothing about HTTP. The handler is the
single place that picks the status code and response shape. Add more exception types as the
app grows; map them all in `main.py`.

---

## 7. Testing

Three test files, each testing at a different level:

```
test_notes_router.py    ← full HTTP stack via TestClient
test_notes_service.py   ← service functions called directly
test_schemas.py         ← validators with parametrize
```

### conftest.py — three fixtures

```python
# tests/conftest.py
def _make_engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="client")          # fakes auth — use for HTTP contract tests
def client_fixture():
    engine = _make_engine()
    def get_session_override():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = lambda: "test-user"
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(name="real_auth_client")  # real JWT — use to test auth itself
def real_auth_client_fixture():
    engine = _make_engine()
    def get_session_override():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(name="db")              # raw session — use for direct service tests
def db_fixture():
    engine = _make_engine()
    with Session(engine) as session:
        yield session
```

### Direct service tests (`test_notes_service.py`)

Call service functions with a real session — no HTTP, no routing, no serialization. Tests
run in under a millisecond each and test exactly one thing:

```python
from app.errors import NoteNotFoundError
from app.schemas import NoteCreate, NoteUpdate
from app.services.notes import note_service


def test_create_persists_note(db):
    note = note_service.create(db, NoteCreate(title="hello"))
    assert note.id is not None
    assert note.title == "hello"


def test_get_raises_for_missing(db):
    with pytest.raises(NoteNotFoundError):
        note_service.get(db, 999)


def test_patch_applies_partial_update(db):
    note = note_service.create(db, NoteCreate(title="original"))
    patched = note_service.patch(db, note.id, NoteUpdate(done=True))
    assert patched.title == "original"   # untouched
    assert patched.done is True
```

Use this style for business-rule tests. Use `TestClient` for HTTP contract tests (status
codes, response shapes, auth behaviour).

### `pytest.mark.parametrize` (`test_schemas.py`)

`parametrize` is pytest's `test.each` — one test function, multiple input/output pairs:

```python
from pydantic import ValidationError
from app.schemas import NoteCreate, NoteUpdate


@pytest.mark.parametrize("title", ["", "   ", "\t", "\n"])
def test_blank_title_rejected(title):
    with pytest.raises(ValidationError):
        NoteCreate(title=title)


@pytest.mark.parametrize("title,expected", [
    ("  hello  ", "hello"),
    (" leading", "leading"),
    ("trailing ", "trailing"),
])
def test_title_whitespace_stripped(title, expected):
    note = NoteCreate(title=title)
    assert note.title == expected


def test_update_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        NoteUpdate(titl="typo")   # extra="forbid" catches this


def test_update_requires_at_least_one_field():
    with pytest.raises(ValidationError):
        NoteUpdate()


@pytest.mark.parametrize("payload,expected_status", [
    ({"title": "valid"}, 201),
    ({"title": ""}, 422),
    ({"title": "   "}, 422),
])
def test_create_endpoint_validation(client, payload, expected_status):
    assert client.post("/notes", json=payload).status_code == expected_status
```

Each tuple becomes one named test run in the output. This replaces writing N
near-identical test functions.

### Mocking with `patch` (`test_notes_router.py`)

When a service calls an external system you don't want that to fire in tests.
`unittest.mock.patch` replaces a name with a `MagicMock` for the duration of a `with` block.

**The rule: patch where the name is *used*, not where it's *defined*.**

```python
# services/notes.py does `import httpx` and then calls `httpx.post`
# so patch it at app.services.notes.httpx.post — not at httpx.post

from unittest.mock import patch


def test_create_calls_webhook(client):
    with patch("app.services.notes.httpx.post") as mock_post:
        r = client.post("/notes", json={"title": "webhook test"})
        assert r.status_code == 201
        # webhook_url is "" in test config so _notify() returns early — not called
        mock_post.assert_not_called()
```

To test with a real webhook URL:

```python
def test_webhook_fires_when_url_set(client, monkeypatch):
    from app import services
    monkeypatch.setattr(services.notes.settings, "webhook_url", "http://example.com/hook")
    with patch("app.services.notes.httpx.post") as mock_post:
        client.post("/notes", json={"title": "x"})
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://example.com/hook"
```

For async functions (common in the real services), use `AsyncMock`:

```python
from unittest.mock import AsyncMock, patch

async def test_async_service():
    with patch("app.services.search.client.embed", new_callable=AsyncMock) as mock:
        mock.return_value = [0.1, 0.2, 0.3]
        result = await search_service.embed("query")
        mock.assert_awaited_once_with("query")
```

### Auth in tests

Override `get_current_user` to skip token validation for tests that aren't testing auth:

```python
app.dependency_overrides[get_current_user] = lambda: "test-user"
```

Use `real_auth_client` (no override) when testing the JWT flow itself:

```python
def test_real_jwt_login_flow(real_auth_client):
    token = real_auth_client.post("/token").json()["access_token"]
    r = real_auth_client.get("/notes", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
```

---

## 8. Authentication: JWT as a dependency

`OAuth2PasswordBearer` extracts the bearer token and wires up the `/docs` "Authorize"
button. `get_current_user` decodes it and returns the subject:

```python
# app/auth.py
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]


def create_access_token(subject: str) -> str:
    return jwt.encode({"sub": subject}, settings.jwt_secret, algorithm="HS256")
```

`CurrentUserDep = Annotated[str, Depends(get_current_user)]` in `dependencies.py` makes
any endpoint require auth with one parameter:

```python
async def list_notes(session: SessionDep, current_user: CurrentUserDep, ...):
```

Because `get_current_user` is a dependency it is:
- **cached per request** — decoded once even if multiple handlers need it
- **overridable in tests** — `dependency_overrides[get_current_user] = lambda: "test-user"`
- **explicit** — you can read which endpoints require auth from their signatures

---

## 9. CORS

The moment a browser calls your API from a different origin (React on `:5173`, API on
`:8000`), the browser enforces CORS. `curl` and `/docs` don't — which is why a request
that works on the command line fails in the browser.

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,   # from config — never hardcoded
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Two rules: `allow_origins=["*"]` and `allow_credentials=True` are **mutually incompatible**
— the browser rejects the combination. If you need cookies or credentials, name explicit
origins. Read them from `settings` so dev and prod differ by env var, not code.

---

## 10. Linters, formatters, and pre-commit

Both production services enforce code style automatically with three tools: **Black**
(formatter), **Pylint** (linter), and **pre-commit** (enforcer). Understanding how they
are configured is useful from day one — you'll see the same `pyproject.toml` sections and
the same pre-commit hook in every service.

### Black — the formatter

Black reformats Python code to a consistent style with no configuration beyond line length.
It is opinionated by design: you never argue about formatting, you just run Black.

```toml
# pyproject.toml
[tool.black]
line-length = 120
target-version = ["py313"]
```

Both services use `line-length = 120`. Run it:

```bash
black app/          # reformat in place
black --check app/  # CI mode: exit 1 if anything would change, don't touch files
```

Black is a formatter, not a linter — it never rejects code, it only rewrites it.

### Pylint — the linter

Pylint catches real bugs (undefined names, wrong argument counts, unreachable code) and
style issues that Black doesn't cover (naming conventions, unused imports, complexity).

Both services configure it in `pyproject.toml`:

```toml
[tool.pylint]
max-line-length = 120       # match Black
disable = [
    "missing-module-docstring",
    "missing-function-docstring",
    "fixme",
]
good-names = ["i", "j", "k", "ex", "Run", "_", "id", "db"]
min-similarity-lines = 8    # duplicate-code threshold
```

Run it:

```bash
pylint app/                         # full report with scores
pylint app/ --fail-under=7          # exit 1 if score < 7 (used in CI)
pylint app/services/notes.py        # single file
```

Pylint scores are 0–10. The UCM service uses `--fail-under=7` in pre-commit. A score of
8–9 is realistic for a healthy codebase; 10 is rare and not the goal.

Common messages you'll see:

| Code | Meaning | Usual fix |
|------|---------|-----------|
| `C0114` | Missing module docstring | Add a one-line module docstring or disable |
| `W0611` | Unused import | Remove the import |
| `R0903` | Too few public methods | Add methods or disable for small data classes |
| `W0718` | Broad exception catch | Catch a specific exception type |
| `R0913` | Too many arguments | Extract a parameter object or disable per function |

Disable a single warning inline when the rule genuinely doesn't apply:

```python
except Exception:  # pylint: disable=broad-except
    pass
```

### pre-commit — enforcing both on every commit

`pre-commit` runs hooks automatically before each `git commit`. If a hook fails, the commit
is blocked. Both services use it to prevent unformatted or lint-failing code from entering
the repo.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-pylint
    rev: v3.0.0
    hooks:
      - id: pylint
        args: [--fail-under=7]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests
        language: system
        types: [python]
        pass_filenames: false
        always_run: true
```

Setup once per clone:

```bash
pip install pre-commit
pre-commit install        # installs the git hook
pre-commit run --all-files  # run manually on everything
```

After `pre-commit install`, every `git commit` runs Pylint and the test suite. A failed
hook aborts the commit and shows what needs fixing.

> **Why this matters:** you will see pre-commit configured in both services. When you clone
> a repo, run `pre-commit install` immediately — otherwise you can commit code that will
> fail CI and block your PR.

### Where to add Black

Black isn't in the current pre-commit config of either service, but adding it is one line:

```yaml
  - repo: https://github.com/psf/black
    rev: 25.1.0
    hooks:
      - id: black
        args: [--line-length=120]
```

---

## Key takeaways

1. **Routers are thin** — three lines: declare, call service, return. All logic is in
   `services/`.
2. **Pydantic validators** (`@field_validator`, `@model_validator`, `extra="forbid"`) enforce
   business rules at the schema boundary, before data reaches the service.
3. **Alembic** applies schema changes to existing databases. `create_all()` is dev-only.
4. **Test at the right level** — `db` fixture for logic, `client` fixture for HTTP
   contracts, `real_auth_client` for auth behaviour.
5. **`parametrize`** replaces N near-identical test functions with one.
6. **Patch where the name is used** (`app.services.notes.httpx.post`), not where it's
   defined. Use `AsyncMock` for coroutines.
7. **`pydantic-settings`** validates config at startup — misconfiguration fails loudly
   rather than mysteriously at request time.
8. **Run `pre-commit install`** after cloning — Black formats, Pylint lints, tests run
   automatically before every commit.

### Concepts to explore further
- Alembic `--autogenerate` limitations (enum columns, server defaults, naming conventions).
- `BackgroundTasks` for fire-and-forget work after the response is sent.
- `mypy` / `pyright` for static type checking beyond what Pylint covers.
- Multiple Uvicorn workers / Gunicorn for using more than one CPU core.
