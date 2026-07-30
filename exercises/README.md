# Exercises

Practice for the [FastAPI docs](../docs/README.md). Each exercise has **failing tests that
describe the target behavior** — your job is to make them pass by editing the starter code
(look for `# TODO`). Completed answers live in [`solutions/`](./solutions/).

| Exercise | Practices | Doc topic |
|----------|-----------|-----------|
| [ex1_search_endpoint](./ex1_search_endpoint/) | query params, filtering, `response_model` | [Topic 1](../docs/session-1.md) |
| [ex4_request_data](./ex4_request_data/) | form fields + file upload (non-JSON request data) | [Topic 1](../docs/session-1.md) |
| [ex2_owner_dependency](./ex2_owner_dependency/) | a `Depends()` that injects a value | [Topic 2](../docs/session-2.md) |
| [ex3_health_and_update](./ex3_health_and_update/) | a new route + DB-backed update with tests | [Topic 3](../docs/session-3.md) |

## How to work an exercise

From the `code/` virtual environment (see [code/README.md](../code/README.md) for setup):

```bash
cd exercises/ex1_search_endpoint
pytest -v          # RED: tests fail — read them to learn the spec
# ...edit the code to satisfy the tests...
pytest -v          # GREEN: all pass -> done

# stuck? compare with the finished version:
cd ../solutions/ex1_search_endpoint && pytest -v
```

The tests are the specification. Read them first — they tell you exactly what to build.
