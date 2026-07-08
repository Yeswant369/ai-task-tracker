# Task Tracker — my submission

A small task tracker built for this exercise: FastAPI backend, in-memory storage,
and a frontend in plain HTML, CSS, and JavaScript (no framework, no build step).

| | |
|---|---|
| **PR 1 — Task CRUD** | https://github.com/Yeswant369/ai-task-tracker/pull/1 |
| **PR 2 — Priority** | https://github.com/Yeswant369/ai-task-tracker/pull/2 (stacked on PR 1) |
| **Write-up** | **[PROJECT.md](PROJECT.md)** — setup for macOS and Windows, how to run it, the design decisions I made, and how I used AI |

**44 tests pass** via `pytest` from `backend/`. Each PR description covers what I
asked the AI for, what I rejected, and the mistakes I caught — including a state-leak
bug in the provided `conftest.py`.

> One gotcha: `pytest -m pr1` and `pytest -m pr2` deselect all 44 tests and exit `5`.
> Those markers belong to the hidden `backend/tests/acceptance/` scorecard suite,
> which isn't in this template. I left my own tests unmarked on purpose rather than
> tag them to make the scorecard look green. See [PROJECT.md](PROJECT.md#tests).

---

<details>
<summary><b>Original exercise brief</b> (unmodified — click to expand)</summary>

# AI-Assisted Full-Stack Interview Exercise

Build a small task tracker in 60 minutes.

You are expected to use AI while working. We evaluate how you use it: what you ask for, what you accept, what you reject, and whether you catch mistakes.

## Stack

- Backend: Python with FastAPI
- Frontend: your choice, inside `frontend/`
- Storage: in-memory only

## PR 1: Task CRUD

Implement task CRUD endpoints:

- `POST /tasks` with body `{"title": "..."}` returns `201` and `{"id", "title", "completed": false}`.
- Empty or missing `title` returns `422`.
- `GET /tasks` returns the list of tasks.
- `PATCH /tasks/{id}` updates `title` and/or `completed`.
- `PATCH /tasks/{id}` for an unknown id returns `404`.
- `DELETE /tasks/{id}` returns `204`.
- `DELETE /tasks/{id}` for an unknown id returns `404`.

Build a minimal frontend that can:

- Show the task list
- Add a task
- Toggle completion

Add your own tests:

- At least 2 unit tests
- At least 1 integration test

## PR 2: Priority

Extend the task tracker with priority support:

- Add `priority` with allowed values: `"low"`, `"medium"`, `"high"`.
- Missing priority uses a sensible default, such as `"medium"`.
- Invalid priority returns `422`.
- Creating a task without priority still works by using a default.
- `GET /tasks?priority=high` filters tasks by priority.
- `GET /tasks?sort=priority` sorts tasks in this order: high, medium, low.

Update the frontend with:

- A priority select when creating or editing tasks
- A priority filter

Add your own tests:

- At least 1 regression test

## Bonus Features

Bonus features are optional and worth less than 10% of the evaluation. Do not skip required PR1 or PR2 behavior to build them.

Pick one or two small enhancements if time allows:

- Dark mode with a visible toggle.
- Subtasks for a task.
- A status bar showing total, completed, and remaining tasks.
- Keyboard shortcuts for adding or toggling tasks.
- One small innovative improvement of your choice that makes the app easier to use.

## Submission

Create your own repository from this template and submit pull request links through this form:

https://forms.gle/ZJPhfrESDGyJdcRb9

1. Click **Use this template** on GitHub and create a new repository under your own account.
2. Clone your new repository locally.
3. Create a branch for PR 1, implement task CRUD, push it, and open a pull request.
4. Create a branch for PR 2 from your completed PR 1 branch, implement priority support, push it, and open a second pull request.
5. If your repository is private, add `chaitanya.mandala@saivaspace.com` as a collaborator.
6. Submit your repository link and both pull request links in the form.

For access issues or questions, email `chaitanya.mandala@saivaspace.com`.

Each PR should use the pull request template and explain how you used AI. Before committing, run:

```bash
git config commit.template .gitmessage
```

Edit the prefilled commit message so it accurately describes what AI helped with, what you rejected or changed, and what you verified.

## Commands

Set up the backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run tests from `backend/` with the virtual environment active:

```bash
pytest
pytest -m pr1
pytest -m pr2
```

</details>
