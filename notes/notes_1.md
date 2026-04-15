# FastAPI Learning Notes

## 0. Project Setup — uv

**uv** is a modern Python package + project manager (written in Rust, by Astral). It replaces `pip`, `virtualenv`, and `pip-tools` in one tool. Much faster than pip.

### Initialize a project
```bash
uv init          # creates pyproject.toml, .python-version, .venv automatically
```
Run this once in your project folder. Creates:
- `pyproject.toml` — your project config + dependency list (replaces requirements.txt)
- `uv.lock` — exact locked versions of all packages (auto-generated, commit this)
- `.venv/` — virtual environment (don't commit this)

### Key commands
```bash
uv add fastapi          # install a package + add to pyproject.toml
uv add "fastapi[standard]"  # install with optional extras (includes uvicorn etc.)
uv remove fastapi       # uninstall + remove from pyproject.toml
uv sync                 # install all deps from uv.lock (use when cloning a repo)
uv run main.py          # run a script inside the project's venv
uv run uvicorn main:app --reload  # run FastAPI dev server
```

### vs pip
| pip | uv |
|-----|----|
| `pip install X` | `uv add X` |
| `pip uninstall X` | `uv remove X` |
| `python -m venv venv` + activate | automatic, use `uv run` |
| `requirements.txt` | `pyproject.toml` + `uv.lock` |

### For this project
```bash
uv init                         # first time setup
uv add "fastapi[standard]"      # installs fastapi + uvicorn + pydantic
uv run uvicorn main:app --reload  # start dev server
```

> `fastapi[standard]` is the recommended install — it includes uvicorn (server) and pydantic (validation) together. No need to install them separately.

---

## 1. Python Type Hints
**Source:** https://fastapi.tiangolo.com/python-types/

Type hints declare what type a variable/parameter should be. Python itself doesn't enforce them at runtime (mostly), but editors and libraries like FastAPI use them heavily.

### Syntax
```python
def func(name: str, age: int = 0) -> str:
    return name
```
- `name: str` — parameter type
- `age: int = 0` — parameter type with default value
- `-> str` — return type

### Simple types
```python
int, float, bool, bytes, str
```

### Generic / Collection types (Python 3.9+)
```python
list[str]           # list of strings
tuple[int, str]     # tuple with an int and a str
set[bytes]          # set of bytes
dict[str, int]      # dict with str keys and int values
```

### Optional / Union types
```python
int | str           # can be int OR str
int | None          # can be int OR None (same as Optional[int])
```

### Any (from typing module)
```python
from typing import Any
x: Any              # can be any type — disables type checking for this var
```

---

## 2. Classes as Type Hints
You can use any class as a type hint. This tells the editor the argument is an instance of that class, giving you autocomplete on its attributes/methods.

```python
class Car:
    color: str
    def drive(self): ...

def start(vehicle: Car):
    vehicle.drive()     # editor knows .drive() exists because of type hint

my_car = Car()          # you still create the object yourself
start(my_car)           # then pass it in
```
> **Key:** the type hint does NOT create the object. It's just a declaration.

---

## 3. Pydantic
**Pydantic** is a data validation library. You define a model class inheriting from `BaseModel`, declare fields with types, and Pydantic handles validation and coercion.

```python
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int
    name: str = "John Doe"          # default value
    signup_ts: datetime | None = None
    friends: list[int] = []

external_data = {
    "id": "123",                    # string "123"
    "signup_ts": "2017-06-01 12:22",
    "friends": [1, "2", b"3"],
}
user = User(**external_data)
# Pydantic automatically coerces:
# "123" → 123 (int)
# "2017-06-01 12:22" → datetime object
# [1, "2", b"3"] → [1, 2, 3] (all int)
# name → "John Doe" (default used since not provided)
```

### What is "coerce"?
Coerce = automatic type conversion. Pydantic tries to convert the value to the declared type.
- `"123"` → `int("123")` → `123` ✓ coerced successfully
- `"abc"` → `int("abc")` → validation error ✗ can't coerce

### Why it matters in FastAPI
FastAPI is built on Pydantic. When you declare a request body as a Pydantic model, FastAPI automatically:
- Validates incoming data
- Coerces types where possible
- Returns a clear error response if validation fails

---

## 4. Annotated (from typing)
`Annotated` wraps a type with extra metadata. Python ignores the metadata, but FastAPI reads it to add behavior.

```python
from typing import Annotated
from fastapi import Query

# Annotated[actual_type, fastapi_object]
def func(age: Annotated[int, Query(gt=0)]):  # gt = greater than 0
    ...
```
FastAPI reads the `Query(gt=0)` object and enforces `age > 0`. Plain strings as metadata do nothing — the metadata must be FastAPI/Pydantic objects that FastAPI knows how to interpret.

> **Note:** `Query`, `Path`, `Body` etc. are FastAPI objects used as metadata. We'll see these in practice when writing endpoints.

---

## 5. How FastAPI Uses Type Hints
FastAPI uses type hints at **runtime** (not just for editor support) to:

| What | How type hints help |
|------|-------------------|
| **Editor support** | Autocomplete, type checking |
| **Define requirements** | Path params, query params, headers, body |
| **Convert data** | Request string → correct Python type |
| **Validate data** | Reject invalid input with clear errors |
| **Generate docs** | Auto OpenAPI/Swagger docs from declarations |

### OpenAPI vs Swagger
- **OpenAPI** — a standard format (JSON/YAML) for describing REST APIs
- **Swagger UI** — a tool that reads an OpenAPI file and renders interactive browser docs
- **FastAPI** — auto-generates the OpenAPI file from your type hints + BaseModel definitions

```
Your type hints + BaseModel
        ↓  FastAPI generates
   OpenAPI JSON spec
        ↓  Swagger UI reads
   Interactive docs at /docs
```

> You write the types once — FastAPI handles docs, validation, and conversion automatically. This becomes clear when you write your first endpoint and visit `/docs`.
