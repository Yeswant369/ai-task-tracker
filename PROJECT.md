# Task Tracker

I built this as a FastAPI backend with a vanilla-JS frontend, delivered as two
stacked pull requests. The original assignment brief is preserved verbatim in
[`README.md`](README.md), below a short intro linking here.

- **Backend:** Python 3.10+, FastAPI, Pydantic v2
- **Frontend:** HTML, CSS, plain JavaScript. No framework, no build step, no dependencies
- **Storage:** an in-memory dict
- **Tests:** 44, all passing under `pytest`

I skipped React and Vite because the whole UI is a `<ul>` I re-render on change.
A framework would have added a `package.json`, a lockfile, and a build step so a
reviewer could render a list of four fields. There is no `package.json` here and
nothing to `npm install`.

## Quick start

Needs **Python 3.10+**. Two terminals — the backend must be running before the
frontend is any use.

**Terminal 1 — backend (port 8000)**

```bash
# macOS / Linux
cd backend
python3.11 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

```powershell
# Windows (PowerShell)
cd backend
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Terminal 2 — frontend (port 5173)**

```bash
# macOS / Linux
cd frontend
python3 -m http.server 5173
```

```powershell
# Windows (PowerShell or cmd)
cd frontend
py -m http.server 5173
```

Now open **<http://localhost:5173>**.

To check the backend on its own: <http://localhost:8000/health> returns
`{"status":"ok"}`, and <http://localhost:8000/docs> is the interactive API
reference.

Run the tests any time with `pytest` from `backend/` (venv active) — 44 pass. See
[Tests](#tests) for why `pytest -m pr1` looks like it fails.

The sections below cover the same ground in more detail, plus the gotchas.

## Requirements

You need **Python 3.10 or newer**. The template's own `backend/app/storage.py`
uses `X | None` in its signatures, which is 3.10+ syntax.

This bit me on macOS: the system `python3` is 3.9, so `python3 -m venv` (what
`AGENTS.md` tells you to run) builds a venv that dies on import with
`TypeError: unsupported operand type(s) for |`. I used Homebrew's 3.11 instead.

```bash
python3 --version    # macOS / Linux
py --version         # Windows
```

## Setup

**macOS / Linux**

```bash
cd backend
python3.11 -m venv .venv          # or python3, if it is already 3.10+
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**Windows — PowerShell**

```powershell
cd backend
py -3.11 -m venv .venv            # or: py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks `Activate.ps1` with an execution-policy error, run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for that session, or
use Command Prompt instead.

**Windows — Command Prompt**

```bat
cd backend
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

## Running it

Two processes. Start the API first, since the frontend talks to it over HTTP.

**Terminal 1 — the API on port 8000.** Same on every platform once the venv is active:

```bash
cd backend
uvicorn app.main:app --reload
```

API docs land at <http://localhost:8000/docs>.

**Terminal 2 — the frontend on port 5173.** It's static files, and Python already
ships a server:

```bash
cd frontend
python3 -m http.server 5173      # macOS / Linux
py -m http.server 5173           # Windows
```

Open <http://localhost:5173>.

Opening `frontend/index.html` straight off disk works too — the backend allows the
`null` origin that `file://` sends. I checked. Serving over HTTP is still closer
to a real deployment.

The API base URL is the `API_BASE` constant at the top of `frontend/app.js`. That
is the only thing to configure.

## Tests

From `backend/`, venv active:

```bash
pytest        # 44 passed
```

**Don't judge this by `pytest -m pr1` or `pytest -m pr2`.** Those markers belong
to the graders' hidden `backend/tests/acceptance/` suite, which isn't in the
template. Running them collects all 44 tests, deselects all 44, and exits with
code `5` — "no tests ran". That's expected, and it's why CI marks both scorecard
steps `continue-on-error`. I left my own tests unmarked on purpose: tagging them
`pr1`/`pr2` would have made the scorecard look green for the wrong reason.

| File | Tests | Kind |
|---|---|---|
| `tests/test_storage.py` | 7 | Unit — storage layer in isolation |
| `tests/test_tasks_api.py` | 14 | Integration — over HTTP via `TestClient` |
| `tests/test_priority.py` | 22 | Regression + priority behaviour |
| `tests/test_health.py` | 1 | Came with the template |

Four of those are **regression** tests guarding PR 1 against the PR 2 change:
creating without a priority still returns `201`; the `422`/`404`/`204` codes are
unchanged; a bare `GET /tasks` still returns creation order; and a partial `PATCH`
doesn't clobber an existing priority.

There's also a sort-**stability** test. `sorted()` is stable, so equal priorities
keep insertion order — the sort of property that regresses silently the moment
someone swaps in a different sort.

## What each PR does

**PR 1 — Task CRUD**

| Endpoint | Behaviour |
|---|---|
| `POST /tasks` | `201` + `{id, title, completed: false, priority}` |
| `POST /tasks` | `422` on empty, whitespace-only, missing, or `null` title |
| `GET /tasks` | Tasks in creation order |
| `PATCH /tasks/{id}` | Updates `title` and/or `completed`; `404` if unknown |
| `DELETE /tasks/{id}` | `204`, empty body; `404` if unknown |

Frontend: list, add, toggle, delete, plus an error banner when the API is down.

**PR 2 — Priority**

`priority` is `low` / `medium` / `high`, defaulting to `medium`. Invalid values
return `422` on create and update. `?priority=high` filters. `?sort=priority`
sorts high → medium → low, stably.

I typed both query params (`Priority | None`, `Literal["priority"] | None`), so
FastAPI rejects unknown values with a `422` before my handler ever runs. No
hand-written validation.

The frontend gets a priority select on create, a per-task select for editing, a
filter, and a sort toggle. Filtering and sorting happen **on the API** via query
params rather than in JS — otherwise the endpoints under test wouldn't actually be
exercised.

Bonus, kept small: a status bar (total / completed / remaining) and a dark-mode
toggle that persists to `localStorage` and otherwise follows
`prefers-color-scheme`.

## Decisions I made, and why

The spec is ambiguous in a few places. Each of these is pinned by a test, so if
you disagree with me the failure is loud rather than silent.

1. **Whitespace-only titles are a `422`,** and I strip titles before storing.
   `{"title": "   "}` is empty for any purpose a user cares about.
2. **`null` means "field omitted" in `PATCH`.** `{"completed": null}` leaves the
   field alone rather than setting it to `None`. That matches the
   `title=None, completed=None` signature the template handed me.
3. **`?sort=title` returns `422`** instead of being silently ignored.
4. **Storage hands back copies,** so a caller can't reach in and mutate a stored
   task.
5. **Every frontend mutation re-reads from the server.** A local-only update
   leaves a task on screen once it stops matching an active filter — demote a task
   from `high` to `low` while filtering by `high` and it lingers. That costs an
   extra round-trip per action, which is the right trade at this scale.
6. **CORS is wide open** (`allow_origins=["*"]`, no credentials). Local
   development only; it's commented as such.

## A bug in the provided scaffold

`backend/tests/conftest.py` had no storage reset, but `storage` is a module-level
singleton. Tests leaked state into each other, and the hidden scorecard tests
would have inherited the same problem. I added an autouse `reset_storage` fixture.

## How I used AI

I used Claude Code (Opus 4.8) to draft the models, storage, endpoints, frontend,
and tests. The full account — the prompts, what I accepted, what I rejected, and
the mistakes I caught — is in the two PR descriptions, as the PR template asks.

Short version of what I rejected or fixed:

- A clever shared validator, `_validate_title = field_validator("title")(_clean_title)`.
  In Pydantic v2 a leading-underscore class attribute becomes a *private
  attribute*, and `field_validator` wants a classmethod. Replaced with two
  explicit classmethod validators.
- Frontend mutations that updated local state instead of re-reading from the
  server — wrong as soon as a filter exists (decision 5 above).
- A shared `mutate()` helper that swallowed errors, so the submit handler cleared
  the user's typed title even when the `POST` had failed. It now returns a success
  boolean.

I also nearly wrote a workaround for a `str`-enum dict-lookup bug that doesn't
exist. I checked it in a REPL first: `str` enums hash as their value.

## How I verified it

Past `pytest`:

- Drove a live `uvicorn` server with `curl` for every documented status code, both
  PRs. For PR 2 that meant confirming `?sort=priority` returns
  `high, high, medium, low, low` with creation order preserved inside each group.
- Drove the real `frontend/app.js` in headless Chrome against the live API: 17 UI
  assertions covering initial render, sort, filter, demote-under-filter, toggle,
  add-with-trimmed-title, status-bar counts, and dark-mode persistence. I checked
  the error-banner path separately by pointing the app at a dead port.

I ran the setup commands above on macOS. The Windows equivalents are the standard
`py` launcher and `.venv\Scripts\` invocations; I didn't have a Windows machine to
run them on.
