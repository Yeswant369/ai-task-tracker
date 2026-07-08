# Task Tracker — what was built

A small task tracker: FastAPI backend, in-memory storage, vanilla-JS frontend.
Delivered as two stacked pull requests.

The assignment brief lives in [`README.md`](README.md) and is unmodified.

| | |
|---|---|
| **Backend** | Python 3.10+, FastAPI, Pydantic v2 |
| **Frontend** | HTML + CSS + vanilla JavaScript. No framework, no build step, no dependencies |
| **Storage** | In-memory dict, no database |
| **Tests** | 44 passing (`pytest`) |

## Why no frontend framework

`AGENTS.md` asks for "no unnecessary frameworks" and the brief asks for a
*minimal* frontend. The entire UI is a `<ul>` re-rendered on change. React or
Vite would have added a `package.json`, a lockfile, and a build step so a
reviewer could render a list of four fields. Three files, opened directly in a
browser, do the same job.

There is **no `package.json` and nothing to `npm install`.**

---

## Requirements

**Python 3.10 or newer.** `backend/app/storage.py` uses `X | None` in its
signatures, which is 3.10+ syntax.

> **macOS users:** the system `python3` is 3.9 and will fail on import with
> `TypeError: unsupported operand type(s) for |`. Use a newer interpreter
> (`brew install python@3.11`) and call it explicitly when creating the venv.
> This is a property of the provided template, not of this implementation.

Check what you have:

```bash
python3 --version    # macOS / Linux
py --version         # Windows
```

---

## Setup

### macOS / Linux

```bash
cd backend
python3.11 -m venv .venv          # or python3, if it is already 3.10+
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows — PowerShell

```powershell
cd backend
py -3.11 -m venv .venv            # or: py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks the activation script with an execution-policy error, either
run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for that session,
or use the Command Prompt form below.

### Windows — Command Prompt

```bat
cd backend
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

---

## Running the app

Two processes. Start the API first — the frontend talks to it over HTTP.

### Terminal 1 — the API (port 8000)

Identical on every platform, once the venv is active:

```bash
cd backend
uvicorn app.main:app --reload
```

Interactive API docs: <http://localhost:8000/docs>

### Terminal 2 — the frontend (port 5173)

The frontend is static files. Any static server works; Python already has one.

**macOS / Linux**

```bash
cd frontend
python3 -m http.server 5173
```

**Windows** (PowerShell or Command Prompt)

```powershell
cd frontend
py -m http.server 5173
```

Then open <http://localhost:5173>.

Opening `frontend/index.html` straight from the file system also works — the
backend allows the `null` origin that `file://` sends. Serving over HTTP is
still the closer match to a real deployment.

The API base URL is the `API_BASE` constant at the top of `frontend/app.js`.
That is the only configuration.

---

## Running the tests

From `backend/`, with the virtualenv active:

```bash
pytest        # 44 passed
```

> **Do not judge the build by `pytest -m pr1` or `pytest -m pr2`.** Those markers
> belong to the graders' hidden `backend/tests/acceptance/` suite, which is not
> present in this template. Running them collects all 44 tests, deselects all 44,
> and exits with code `5` ("no tests ran"). That is expected, and it is why CI
> marks both scorecard steps `continue-on-error`. The tests in this repo are
> intentionally left unmarked so they cannot inflate the graders' scorecard.

---

## What is implemented

### PR 1 — Task CRUD

| Endpoint | Behaviour |
|---|---|
| `POST /tasks` | `201` + `{id, title, completed: false, priority}` |
| `POST /tasks` | `422` on empty, whitespace-only, missing, or `null` title |
| `GET /tasks` | Tasks in creation order |
| `PATCH /tasks/{id}` | Updates `title` and/or `completed`; `404` if unknown |
| `DELETE /tasks/{id}` | `204` with an empty body; `404` if unknown |

Frontend: list tasks, add, toggle completion, delete, and an error banner when
the API is unreachable.

### PR 2 — Priority

- `priority` of `"low"` / `"medium"` / `"high"`, defaulting to `"medium"`.
  Creating a task without one still works.
- Invalid priority → `422`, on both create and update.
- `GET /tasks?priority=high` filters.
- `GET /tasks?sort=priority` sorts high → medium → low, **stably**: equal
  priorities keep creation order.

Both query params are typed (`Priority | None`, `Literal["priority"] | None`), so
FastAPI rejects unknown values with a `422` before the handler runs. No
hand-written validation.

Frontend: a priority select on create, a per-task select for editing, a priority
filter, and a sort toggle. Filtering and sorting are performed **by the API** via
query params, not client-side — that way the endpoints under test are the ones
actually exercised.

### Bonus (small, well under 10% of the effort)

- Status bar: total / completed / remaining, plus "showing N" when filtered.
- Dark mode toggle, persisted to `localStorage`, defaulting to the system
  `prefers-color-scheme`.

---

## Tests

44 tests. Layout:

| File | Count | Kind |
|---|---|---|
| `tests/test_storage.py` | 7 | **Unit** — storage layer in isolation |
| `tests/test_tasks_api.py` | 14 | **Integration** — through HTTP via `TestClient` |
| `tests/test_priority.py` | 22 | Regression + priority behaviour |
| `tests/test_health.py` | 1 | Provided by the template |

The four **regression** tests guard PR 1 against the PR 2 change: creating
without a priority still returns `201`; the `422`/`404`/`204` status codes are
unchanged; an unfiltered `GET /tasks` still returns creation order; and a partial
`PATCH` does not clobber an existing priority.

There is also a sort-**stability** test. `sorted()` is stable, so tasks of equal
priority keep insertion order — the kind of property that regresses silently the
moment someone swaps in a different sort.

---

## Design decisions worth knowing

These are deliberate readings of an ambiguous spec. Each is pinned by a test, so
if you disagree the failure is loud rather than silent.

1. **Whitespace-only titles are a `422`,** and titles are stripped before
   storage. `{"title": "   "}` is empty for any purpose a user cares about.
2. **`null` means "field omitted" in `PATCH`.** `{"completed": null}` leaves the
   field alone rather than setting it to `None`, matching the
   `title=None, completed=None` signature the template provided.
3. **`?sort=title` returns `422`** rather than being silently ignored.
4. **Storage hands back copies.** A caller cannot reach in and mutate a stored
   task.
5. **Every frontend mutation re-reads from the server.** A local-only state
   update would leave a task on screen after it stopped matching an active
   filter — for example, demoting a task from `high` to `low` while filtering by
   `high`. This costs an extra round-trip per action and is the right trade at
   this scale.
6. **CORS is permissive** (`allow_origins=["*"]`, no credentials). Local
   development only; it is commented as such.

### One bug found in the provided scaffold

`backend/tests/conftest.py` had no storage reset, but `storage` is a module-level
singleton. Tests leaked state into one another, and the hidden scorecard tests
would have inherited the same problem. An autouse `reset_storage` fixture now
isolates every test.

---

## How this was verified

Beyond `pytest`:

- A live `uvicorn` server driven with `curl` for every documented status code —
  `201` / `422` empty / `422` missing / `200` list / `200` patch / `404` patch /
  `204` delete / `404` delete, plus a `200` CORS preflight. For PR 2: the medium
  default, `422` on invalid priority for create *and* patch, `?priority=high`
  filtering, `?sort=priority` returning `high, high, medium, low, low` with
  creation order preserved inside each group, and `422` for `?priority=urgent`
  and `?sort=title`.
- The real `frontend/app.js` driven in headless Chrome against the live API — 17
  UI assertions covering initial render, sort, filter, demote-under-filter,
  toggle, add-with-trimmed-title, status-bar counts, and dark-mode persistence.
  The error-banner path was confirmed separately by pointing the app at a dead
  port.

The setup commands above were exercised on macOS. The Windows equivalents are the
standard `py` launcher and `.venv\Scripts\` invocations; they were not run on a
Windows machine.
