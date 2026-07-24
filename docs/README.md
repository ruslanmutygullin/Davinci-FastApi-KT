# FastAPI for JS Developers — Concepts & Reference

A reference guide teaching JavaScript/Node developers the **theory and mechanics** behind
building and maintaining FastAPI projects. Python basics are assumed.

This is organized as three topic areas, each a self-contained read. They build on one
another, but each one leads with *how things actually work* rather than a step-by-step
build. Code is there to illustrate the concept, not to be typed in order.

## Topics

| # | File | What it explains | Runnable code |
|---|------|------------------|---------------|
| 1 | [session-1.md](./session-1.md) | The request lifecycle, ASGI, type-driven validation, Pydantic, `Annotated` | [`code/topic-1`](../code/topic-1/) |
| 2 | [session-2.md](./session-2.md) | Project architecture, ORMs & sessions, dependency injection | [`code/topic-2`](../code/topic-2/) |
| 3 | [session-3.md](./session-3.md) | Config, errors, testing, CORS, JWT auth, Docker, async, troubleshooting | [`code/topic-3`](../code/topic-3/) |
| — | [glossary.md](./glossary.md) | Every term (ASGI, coercion, session, event loop, …) with a Node analogy | — |

Prefer to learn by doing? Each topic has a matching **runnable app** in
[`code/`](../code/README.md) and a hands-on **exercise** in
[`exercises/`](../exercises/README.md) (failing tests you make pass).

Stuck on a specific error? Jump to the
[troubleshooting table](./session-3.md#8-troubleshooting-symptoms-js-developers-hit-first).

## The mental model: what FastAPI *is*

FastAPI is not a server. It's a framework that produces an **[ASGI](./glossary.md#asgi)
application** — an async callable that a server ([Uvicorn](./glossary.md#uvicorn)) invokes
for each request. Understanding this split is the single most useful thing for a Node
developer, because in Node the framework (Express) and the server (`http.createServer`) are
often blurred into one object.

> New to the Python web vocabulary? A [glossary](./glossary.md) defines every term
> (ASGI, coercion, session, event loop, …) with a Node analogy. Terms link to it on first
> use.

```
                 HTTP request
                      │
                      ▼
        ┌──────────────────────────┐
        │  Uvicorn (ASGI server)   │   ← the process that listens on a port
        │  - parses HTTP           │     (analogous to Node's http server)
        │  - manages the event loop│
        └────────────┬─────────────┘
                     │ calls
                     ▼
        ┌──────────────────────────┐
        │  FastAPI app (ASGI app)  │   ← your framework object, `app`
        │  - routing               │
        │  - validation            │
        │  - dependency injection  │
        │  - serialization         │
        └──────────────────────────┘
```

In Node terms: **Uvicorn ≈ the `http` server + event loop, FastAPI ≈ Express**. You start
Uvicorn and *point it at* your FastAPI app: `uvicorn main:app`.

## Three ideas that carry the whole framework

Everything else is detail. If you understand these three, FastAPI is mostly predictable:

1. **Type hints are executable contracts.** In TypeScript, types vanish at runtime. In
   FastAPI, the type annotations on your function parameters *are* the validation,
   parsing, and documentation. This is the biggest mental shift.

2. **`Depends()` is a resolution graph, not middleware.** Dependencies are values that
   FastAPI computes and injects. They form a graph, are cached per-request, and are
   *overridable* — which is what makes the whole thing testable.

3. **Async is about concurrency, not speed.** `async def` lets one worker handle many
   waiting requests. It does not make CPU work faster, and a blocking call inside `async`
   stalls everything.

## Rosetta Stone (Node ↔ FastAPI)

| Node / Express / Nest | FastAPI | Note |
|-----------------------|---------|------|
| `http.createServer` + event loop | Uvicorn (ASGI server) | the runtime |
| Express `app` | FastAPI `app` | the framework object |
| `app.get("/", handler)` | `@app.get("/")` | decorator vs. method call |
| TS interface (compile-time) + Zod (runtime) | Pydantic `BaseModel` | one tool, runtime-enforced |
| `req.params.id` (always a string) | `id: int` param (parsed & validated) | types do the work |
| Express middleware (mutates `req`) | `Depends()` (returns a value) | injection, not mutation |
| Nest `@Injectable()` + DI container | `Depends(get_thing)` | closest analogue |
| Prisma / Drizzle client | SQLModel / SQLAlchemy | ORM + session |
| `prisma migrate` | Alembic | schema migrations |
| Jest + Supertest | pytest + `TestClient` | tests hit the app in-process |
| `dotenv` + zod env schema | `pydantic-settings` | validated config |
| `throw new HttpException()` (Nest) | `raise HTTPException()` | maps to HTTP status |
| `server.listen()` / `server.close()` | `lifespan` async context manager | startup/shutdown |
| `cors` npm middleware | `CORSMiddleware` | same browser rules, one config block |
| Passport / `jsonwebtoken` + guards | `OAuth2PasswordBearer` + a `Depends` | auth is just a dependency |

## A note on `async`

Python has both `def` and `async def` route handlers, and FastAPI supports both — this
surprises Node developers, where everything is async by default. The rule:

- Use `async def` when the work inside is itself async (async DB driver, `httpx`, etc.).
- Use plain `def` when the work is blocking (a sync DB driver, CPU work). FastAPI runs
  `def` handlers in a **thread pool** so they don't block the event loop.

The danger case is a *blocking* call inside an `async def` — that runs on the event loop
and freezes every other in-flight request. This is covered in detail in Topic 3.
