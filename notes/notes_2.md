# Concurrency and async/await
**Source:** https://fastapi.tiangolo.com/async/

---

## 1. Asynchronous Code

Asynchronous code lets the system **not wait** for slow tasks to finish. Instead of sitting idle, it moves on to other work and comes back to check on the slow task later.

The "slow tasks" are **I/O bound operations** — things where the CPU has nothing to compute and is just waiting:
- Network requests
- Database queries
- File reads/writes
- Waiting for user input

This switching between tasks happens in microseconds on a **single thread**. It looks like parallelism, but it's not — one thread is rapidly switching between tasks, doing a little bit of each.

---

## 2. Synchronous vs Asynchronous

**Synchronous:** functions execute one after another. Each waits for the previous to finish.

**Asynchronous:** functions can pause (at `await`) and let others run. The system keeps track of all running tasks and switches between them.

```python
# Synchronous — sequential, 2 seconds total
result1 = slow_task_1()   # waits 1s
result2 = slow_task_2()   # waits 1s

# Asynchronous — concurrent, 1 second total
result1, result2 = await asyncio.gather(slow_task_1(), slow_task_2())
```

---

## 3. `async def` and `await`

- `async def` defines a function that can pause and resume (a coroutine)
- `await` pauses execution of that function until the awaited thing finishes
- `await` can ONLY be used inside an `async def` function

```python
async def get_data():
    result = await some_slow_io()   # pauses here, system does other work
    return result                    # resumes when result is ready
```

---

## 4. Coroutines

A coroutine = the object returned by an `async def` function. It's a function that:
- Starts and finishes
- Might pause in between (at `await` points)

Similar to goroutines in Go. That's all — nothing more complicated than that.

---

## 5. Concurrency vs Parallelism

### Concurrency (async)
- **One thread** switching between multiple tasks
- Best for **I/O bound** work (waiting on network, database, files)
- Like ordering a burger, getting a number, and doing other things while it cooks
- If a slow task finishes but the system is busy with another task, it completes the current task first, then comes back

### Parallelism (multiprocessing)
- **Multiple cores** running tasks simultaneously
- Best for **CPU bound** work (math, image processing, ML training)
- Like having multiple cooks each making a burger at the same time
- Parallel doesn't always mean better — for I/O tasks, threads just sit idle waiting

### Combined (FastAPI)
- FastAPI can do **both** — async for I/O + parallelism for CPU work
- This is why it's popular for ML/AI APIs: serve requests concurrently, run models in parallel

---

## 6. Core vs Thread vs Interpreter

| Term | What it is | Type |
|------|-----------|------|
| **CPU/Processor** | The physical chip | Hardware |
| **Core** | A processing unit inside the CPU (modern CPUs have 8-16) | Hardware |
| **Thread** | A sequence of instructions a core works through | Software |
| **Interpreter** | Translates and runs your Python code | Software |

One core can handle many threads by switching between them (OS manages this). Python's GIL (Global Interpreter Lock) limits the default interpreter to one thread executing Python code at a time, even with multiple cores.

---

## 7. Python async vs Node.js

Both use a **single-threaded event loop** for async code. Very similar concept.

Key difference:
- **Node.js** — async by default. Everything is async. Can't easily do CPU-heavy work without blocking.
- **Python** — async is opt-in (`async/await`). But Python can also spawn real OS processes to use multiple cores for CPU work (parallelism). FastAPI combines both.

---

## 8. Uvicorn

Uvicorn is an **ASGI server**. It:
- Listens on a port for HTTP requests
- Passes them to your FastAPI app
- Handles the event loop (`asyncio.run()` internally)

FastAPI = the chef (defines what to do). Uvicorn = the door (receives requests).

```bash
uvicorn main:app --reload
# main   = the file main.py
# app    = the FastAPI() variable in that file
# --reload = restart on code changes (dev only)
```

Using uvicorn

uvicorn main:app --reload --port 8000
main:app — file main.py, variable app (required)
--reload — restart server when code changes (dev only)
--port 8000 — port number (8000 is default, so optional)
That's it. The main:app part is required, everything else has defaults.

---

## 9. Starting Async Code

### In regular Python
Someone has to start the event loop. That's `asyncio.run()`:
```python
import asyncio

async def main():
    await some_async_function()

asyncio.run(main())  # starts the event loop, runs the first coroutine
```

### In FastAPI
You never call `asyncio.run()`. Uvicorn does it for you. You just define your functions:
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "hello"}
```

---

## 10. Three Ways to Call Async Functions

### Sequential (`await`)
```python
result1 = await one()    # waits 1s
result2 = await two()    # waits 1s
# total: 2 seconds
```

### Concurrent (`gather`)
```python
r1, r2 = await asyncio.gather(one(), two())
# both run concurrently — total: 1 second
# gather waits for ALL to finish before returning
# even if one() finishes in 0.5s, it waits for two() (1s)
```

### Fire and forget (`create_task`)
```python
asyncio.create_task(one())
# schedules one() on the event loop, doesn't wait
# continues immediately, one() runs in background
# no extra thread — same event loop picks it up
```

---

## 11. How FastAPI Handles `def` vs `async def`

| You write | FastAPI does |
|-----------|-------------|
| `async def endpoint()` | Runs directly on the main async event loop |
| `def endpoint()` (plain) | Runs in a **threadpool** (~40 threads) so it doesn't block the event loop |

If 100 plain `def` requests come in at once:
- ~40 run simultaneously across threadpool threads
- The rest queue up and wait for a thread to free up

`async def` has no such limit — all run on the single event loop. More efficient for I/O work.

**Rule of thumb:**
- Library supports `await` -> use `async def`
- Library does NOT support `await` (blocking) -> use plain `def`
- Not sure -> use plain `def` (FastAPI protects you with the threadpool)

---

## 12. Automatic Docs — How They Work

```
Your type hints + Pydantic models
        ↓  FastAPI reads these at startup
   OpenAPI JSON spec (auto-generated at /openapi.json)
        ↓  Swagger UI reads this JSON
   Interactive docs at /docs
```

Nobody writes the docs manually. FastAPI inspects your code — types, models, routes — and generates an OpenAPI spec.

- **`/docs`** — interactive docs by **Swagger UI**
- **`/redoc`** — alternative docs by **ReDoc** (same OpenAPI spec, different UI)

### Minimal FastAPI server

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "hello world"}
```

Run with `fastapi dev` or `uvicorn main:app --reload` — then visit `/docs` or `/redoc`.

---

## 13. ASGI — What It Is

ASGI = **Asynchronous Server Gateway Interface**. A standard that defines how a server talks to a Python web framework.

- **Server** (uvicorn) receives raw HTTP → passes to framework via ASGI protocol
- **Framework** (FastAPI) processes it → returns response via ASGI protocol

Older version: WSGI (synchronous, used by Flask). ASGI supports async.

---

## 14. Uvicorn Internals (Simplified)

Uvicorn internally does something like:

```python
async def serve():
    while True:
        request = await wait_for_next_request()  # pauses until request comes
        await app(request)                        # calls your FastAPI app

asyncio.run(serve())   # starts event loop, runs forever
```

- `app` is your FastAPI instance — it's a **callable async function** (follows ASGI standard)
- `serve()` never finishes — loops forever listening for requests
- Ctrl+C stops it

---

## 15. `fastapi dev` Command

```bash
fastapi dev
```

A CLI shortcut that comes with `fastapi[standard]`. It just runs `uvicorn main:app --reload` with sensible defaults. Nothing more.

With uv: `uv run fastapi dev`

---

## 16. Installing FastAPI

```bash
pip install "fastapi[standard]"    # recommended — includes uvicorn, pydantic, etc.
pip install fastapi                # minimal, no extras
```

With uv: `uv add "fastapi[standard]"`

---

## 17. Request Flow — From HTTP to Response

### Decorators and Path Operation Functions

```python
@app.get("/page")          # decorator — registers the route (runs ONCE at startup)
async def read_page():     # path operation function — runs on each request
    return {"msg": "hi"}
```

The decorator does NOT run per request. It runs **once at startup** to register: "`/page` + GET = `read_page`". After that, only the function runs.

### Full request flow

1. Client sends `GET /page` to port 8000
2. **Uvicorn** (listening on port 8000) receives the raw HTTP request
3. Passes it to **FastAPI `app`**
4. FastAPI looks up its route table: `/page` + `GET` → `read_page`
5. Runs `read_page()`
6. Takes the return value, converts to JSON HTTP response
7. **Uvicorn** sends response back to the client

---

## 18. Starlette

Starlette is the **web framework FastAPI is built on**. FastAPI is literally a subclass of Starlette.

```
Uvicorn  →  Starlette  →  FastAPI  →  Your code
(server)    (web framework)  (API framework)   (routes/logic)
```

- **Starlette** handles low-level stuff — routing, requests, responses, WebSockets, middleware
- **FastAPI** adds on top — type validation, automatic docs, Pydantic integration

When docs say "using an option from Starlette" (like `:path`), it means FastAPI inherited that feature. No need to learn Starlette separately.

---

## 19. Path Parameters

**Source:** https://fastapi.tiangolo.com/tutorial/path-params/

### Basic usage
```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

- `{item_id}` in the route becomes the function argument `item_id`
- Type hint `int` gives **data conversion** (`"3"` → `3`) and **validation** (rejects `"foo"` or floats with a 422 error)

### Route order matters

FastAPI checks routes **top to bottom**, stops at first match. Put specific routes before generic ones:

```python
@app.get("/users/me")         # first — specific
async def read_user_me(): ...

@app.get("/users/{user_id}")  # second — generic
async def read_user(user_id: str): ...
```

If reversed, `/users/me` would match `{user_id}` with `user_id="me"`.

### Predefined values with Enum

```python
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    return {"model": model_name.value}
```

- Only values defined in the enum are allowed — anything else returns a **422 error** automatically
- Enum values show up in `/docs`
- `model_name` is the enum member, `model_name.value` is the string

### Path parameters containing paths

```python
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
```

`:path` tells Starlette the parameter can contain `/` slashes — so `/files/home/john/file.txt` works instead of failing.
