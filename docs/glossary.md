# Glossary

Terms used throughout these docs, defined for a developer coming from the JavaScript /
Node world. Anchors are stable — other docs link directly to them (e.g.
`glossary.md#asgi`).

### ASGI
**Asynchronous Server Gateway Interface.** The Python standard that defines how an async
web server talks to an async web application. An ASGI *application* is a single async
callable `async def app(scope, receive, send)`. FastAPI produces one; Uvicorn calls it.
The async successor to the older, synchronous WSGI. *Node analogy:* the contract between
`http.createServer` and your request handler, standardized so any server can run any app.

### ASGI server
The process that listens on a TCP port, parses raw HTTP, runs the event loop, and invokes
your ASGI application once per request. **Uvicorn** is the common choice. *Node analogy:*
the `http` server plus the event loop, as a separate concern from your framework.

### Coercion
Pydantic converting an input value to the declared type when it's safe to do so — e.g. the
string `"5"` from a URL becomes the int `5`, `"true"` becomes `True`. Distinct from
**validation** (checking) though they happen together. Coercion is stricter for JSON bodies
(where a real number exists) than for query/path params (where everything arrives as a
string).

### Composition root
The single place where an application is *assembled* — where the framework object is
created and all the pieces (routers, config, lifespan) are wired together. In these docs
that's `app/main.py`. *Node analogy:* your top-level `server.js` that imports and mounts
all the routers.

### Coroutine
The object returned by calling an `async def` function. It represents work that can be
paused and resumed. It does nothing until *awaited* or scheduled on the **event loop**.
*Node analogy:* very close to a `Promise`, but a coroutine doesn't start running until
awaited, whereas a Promise starts eagerly.

### Dependency (in the `Depends` sense)
A value FastAPI computes and injects into a handler, declared with `Depends(func)`. Not
middleware — it *returns a value* rather than mutating a request object. Dependencies form
a graph, are cached per request, support setup/teardown via `yield`, and can be overridden
in tests. See [Topic 2](./session-2.md#3-dependency-injection-the-core-of-fastapi).

### Dependency injection (DI)
The pattern of *asking for* the things you need (as parameters) and letting the framework
*supply* them, rather than constructing or importing them yourself. Makes code declarative
and — crucially — testable, because what gets supplied can be swapped. *Node analogy:*
Nest's DI container; there's no direct Express equivalent.

### Engine (SQLAlchemy/SQLModel)
The application-wide object that manages the pool of database connections. Created once.
Not a connection itself — a factory and pool. *Node analogy:* the Prisma client instance
you construct once and reuse everywhere.

### Event loop
The single-threaded scheduler that runs async code: it starts a coroutine, and when that
coroutine `await`s I/O, the loop parks it and runs another. This is how one worker serves
many concurrent requests. *Node analogy:* identical concept to Node's event loop.

### Lifespan
An async context manager passed to `FastAPI(lifespan=...)` that runs startup code before
`yield` and shutdown code after. App-scoped setup/teardown. *Node analogy:* the code around
`server.listen()` and `server.close()`.

### OpenAPI
The specification (formerly called Swagger) describing an HTTP API's endpoints, parameters,
and schemas as a machine-readable document. FastAPI generates it automatically from your
type hints and serves it at `/openapi.json`, with interactive UIs at `/docs` and `/redoc`.

### ORM
**Object-Relational Mapper.** A library that maps database rows to language objects so you
work with classes instead of raw SQL. SQLAlchemy and SQLModel are the common Python choices.
*Node analogy:* Prisma, Drizzle, TypeORM.

### Pydantic
The runtime data-validation library at FastAPI's core. A `BaseModel` subclass is
simultaneously a type annotation, a runtime validator/coercer, and an OpenAPI schema. See
[Topic 1](./session-1.md#4-pydantic-types-that-exist-at-runtime). *Node analogy:* a
TypeScript interface *and* a Zod schema fused into one object, enforced at runtime.

### Router (`APIRouter`)
A mountable group of related endpoints with a shared path prefix and tags, included into the
main app via `app.include_router(...)`. *Node analogy:* `express.Router()`.

### Serialization
Converting your handler's return value (a Python object) into the JSON sent to the client,
governed by `response_model`. The outbound counterpart to validation.

### Session (database)
A short-lived unit of work that tracks loaded/modified objects and flushes them to the
database in a transaction on `commit()`. Not thread-safe; created one-per-request. *Note:*
unrelated to an HTTP/login "session." See
[Topic 2](./session-2.md#the-session--a-unit-of-work).

### Unit of work
The design pattern a database **session** implements: accumulate changes in memory, then
commit them together as one atomic transaction, rather than writing each change immediately.

### Uvicorn
The **ASGI server** these docs use to run the FastAPI app: `uvicorn app.main:app`. *Node
analogy:* the runtime that listens and dispatches — the `node server.js` half of the stack.

### Validation
Pydantic checking that input conforms to the declared types and constraints, rejecting
mismatches with a **422** before your handler runs. Distinct from but simultaneous with
**coercion**. See [Topic 1](./session-1.md#4-pydantic-types-that-exist-at-runtime).

### WSGI
The older, *synchronous* Python web-server standard that **ASGI** succeeds. Frameworks like
Flask and Django (classic) are WSGI; FastAPI is ASGI, which is what enables `async`.

### 422 (Unprocessable Entity)
The HTTP status FastAPI returns automatically when request **validation** fails. The body
lists each failing field, its location (`loc`), and why. Distinct from `400 Bad Request`,
which you'd raise for semantic errors your own code detects.
