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
