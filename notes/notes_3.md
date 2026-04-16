# Query Parameters
**Source:** https://fastapi.tiangolo.com/tutorial/query-params/

---

## 1. What is a Query Parameter

Any function parameter that is **not** in the route path is automatically a **query parameter**.

```python
@app.get("/items")
async def get_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

Called as: `/items?skip=5&limit=20`

- `?` starts the query string
- `key=value` pairs separated by `&`
- Names in URL must **exactly match** function parameter names

---

## 2. Required vs Optional vs Default

```python
# Required — no default, must be provided or 422 error
async def func(query: int): ...

# Default value — optional, uses 0 if not provided
async def func(query: int = 0): ...

# Optional (can be None) — MUST have `= None` as default
async def func(query: int | None = None): ...

# STILL REQUIRED — no default value even though None is allowed type
async def func(query: int | None): ...
```

`int | None` only means "type can be int or None". The `= None` is what makes it optional.

If you want query to not be required, define type hint + default as None 

---

## 3. Type Conversion & Validation

Query params get the same type conversion and validation as path params:

- `/items?skip=3` → `skip` becomes int `3`
- `/items?skip=foo` → **422 validation error**
- Bool accepts specific values only:
  - **True**: `true`, `True`, `1`, `yes`, `on`
  - **False**: `false`, `False`, `0`, `no`, `off`
  - Anything else → **422 error** (stricter than Python's built-in `bool()`)

---

## 4. Extra / Missing Query Params

| Scenario | Result |
|----------|--------|
| Required param missing from URL | 422 error |
| Extra param in URL not in function | Ignored silently |
| Param name in URL ≠ function param name | 422 (required param missing) |

---

## 5. Mixing Path and Query Params

FastAPI tells them apart by the route — if the name is in `{}` it's a path param, otherwise it's a query param.

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int, details: bool = False):
    return {"user_id": user_id, "details": details}
```

- `user_id` → **path param** (in route `{user_id}`)
- `details` → **query param** (not in route)
- Called as: `/users/42?details=true`

---

## 6. Trailing Slash

```python
@app.get("/page/")    # with trailing slash
@app.get("/page")     # without
```

If route has trailing `/`, calling without it triggers a **307 redirect** to the version with `/`. Best practice: skip the trailing slash.

---

## 7. HTTP Methods

```python
@app.get(...)       # GET
@app.post(...)      # POST
@app.put(...)       # PUT
@app.delete(...)    # DELETE  (not @app.del — del is a Python keyword)
@app.patch(...)     # PATCH
```

## 8. Multiple path and query parameters

We can declare multiple path parameters and query parameters at the same time, FastAPI knows which is which, regarldess of the order in which they were defined. They will be detected by name.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
```

---

## 9. Understanding the Basics

### What is a Server?

A program running on a computer that **listens for requests and sends responses**. FastAPI + Uvicorn together make a server — Uvicorn listens on a port, FastAPI routes and processes the request, your functions handle the logic.

### What is an API?

A loose, umbrella term. It represents the **complete external contract** of your app — the collection of endpoints, what data they accept, what they return, how to authenticate, what errors look like, and the rules around it all. When someone says "build an API," they mean write all of it.

An API includes:
- **Endpoints** — all the routes + HTTP methods
- **Data format** — what shape request/response data takes (JSON)
- **Validation & rules** — constraints, rate limits, permissions
- **Auth** — who can call what
- **Error responses** — what happens when things go wrong
- **Status codes** — 200 OK, 404 Not Found, 422 Validation Error, etc.

All of this is defined in your endpoints and path operation functions. The API isn't a separate thing — it **emerges from** your code. It's the external face of what you write.

### Request Body vs Response Body

```
Client  ——sends data——→  Server     = Request Body  (JSON the client sends)
Client  ←——sends data——  Server     = Response Body  (JSON the server returns)
```

An HTTP request has headers (metadata) and body (actual data). GET requests usually have no body. POST/PUT requests usually do.

### Why `app = FastAPI()`?

One central object that collects and manages all routes. Uvicorn needs one thing to hand requests to — that's `app`. It holds the route table, middleware, docs config, everything.

### Why decorators?

Decorators are just a clean way to register a function to a route:

```python
# These two are equivalent:
@app.get("/page")
async def read_page():
    return {"msg": "hi"}

# vs (hypothetical without decorator)
async def read_page():
    return {"msg": "hi"}
app.add_route("/page", read_page, method="GET")
```

The decorator internally calls `app.add_route(...)` for you. It's syntactic sugar — runs once at startup to register the route.

---

## 10. Request Body
**Source:** https://fastapi.tiangolo.com/tutorial/body/

### What is a Request Body?

Data sent by the client to the server. GET requests usually don't have one. POST/PUT/PATCH requests usually do.

### Defining a Request Body with BaseModel

Use a Pydantic `BaseModel` to define the shape of the request body:

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    description: str | None = None

@app.post("/items")
async def create_item(item: Item):
    return {"name": item.name, "price": item.price}
```

- `BaseModel` = a class that defines a data structure with typed fields
- Pydantic validates and converts the incoming JSON automatically
- Invalid data → **422 error** with clear details

### How FastAPI tells parameters apart

| Parameter type hint | FastAPI treats it as |
|---|---|
| Name matches `{route}` | **Path param** |
| `BaseModel` subclass | **Request body** |
| Everything else | **Query param** |

```python
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    # item_id → path param (in route)
    # item    → request body (BaseModel)
    # q       → query param (everything else)
    return {"item_id": item_id, **item.dict()}
```

### BaseModel vs Enum

- **Enum** = a fixed list of allowed values. Like a dropdown — pick one.
- **BaseModel** = a data structure with multiple fields. Like a form — fill in fields.

---

## 11. Query Parameter Validations
**Source:** https://fastapi.tiangolo.com/tutorial/query-params-str-validations/

### Adding validations with `Annotated` + `Query()`

```python
from typing import Annotated
from fastapi import Query

@app.get("/items")
async def read_items(
    q: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
):
    return {"q": q}
```

Available validations: `min_length`, `max_length`, `pattern` (regex), `title`, `description`.

### Default values

```python
q: Annotated[str, Query(min_length=3)] = "fixedquery"
```

Don't set default in both places — this is **not allowed**:
```python
q: Annotated[str, Query(default="rick")] = "morty"  # error — ambiguous
```

### List query params

`Query()` is required for list params, otherwise FastAPI treats it as a request body:

```python
# Correct — called as /items?q=foo&q=bar
q: Annotated[list[str], Query()] = ["foo", "bar"]

# Without Query() — FastAPI thinks it's a request body
q: list[str] = ["foo", "bar"]  # wrong
```

### Other useful Query() options

```python
# alias — when URL param name isn't valid Python (has dash, space, etc.)
q: Annotated[str | None, Query(alias="item-query")] = None
# Called as: /items?item-query=hello

# deprecated — shows as deprecated in /docs but still works
q: Annotated[str | None, Query(deprecated=True)] = None

# include_in_schema — hides param from /docs entirely
q: Annotated[str | None, Query(include_in_schema=False)] = None
```

---

## 12. Path Parameter Validations
**Source:** https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/

`Path()` works exactly like `Query()` but for path parameters — same metadata (`title`, `description`), same pattern.

```python
from fastapi import Path

@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="Item ID", ge=1, le=1000)],
):
    return {"item_id": item_id}
```

### Numeric validations (work in both `Path()` and `Query()`)

| Operator | Meaning |
|---|---|
| `gt` | greater than |
| `ge` | greater than or equal |
| `lt` | less than |
| `le` | less than or equal |

Works for `int` and `float`.

---

## 13. Query Parameter Models
**Source:** https://fastapi.tiangolo.com/tutorial/query-param-models/

Group related query params into a Pydantic model for reuse across multiple endpoints.

```python
from pydantic import BaseModel, Field
from typing import Literal, Annotated
from fastapi import Query

class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []

@app.get("/items")
async def get_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query
```

- `Query()` is required — without it, FastAPI treats `BaseModel` as a request body
- `Field()` inside BaseModel = same as `Query()` for validation (`gt`, `le`, etc.)
- `Literal["a", "b"]` = inline enum, only allows those exact values
- `model_config = {"extra": "forbid"}` — rejects any query param not defined in the model (by default extras are ignored)

Use when multiple endpoints share the same query params. Otherwise regular individual params are fine.