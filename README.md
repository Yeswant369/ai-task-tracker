# Application stats:

Built a small task tracker as part of test



## Stack

- Backend: Python with FastAPI
- Frontend: your choice, inside `frontend/`
- Storage: in-memory only

## PR 1: Task CRUD

Implemented the task CRUD endpoints:

- `POST /tasks` with body `{"title": "..."}` returns `201` and `{"id", "title", "completed": false}`.
- Empty or missing `title` returns `422`.
- `GET /tasks` returns the list of tasks.
- `PATCH /tasks/{id}` updates `title` and/or `completed`.
- `PATCH /tasks/{id}` for an unknown id returns `404`.
- `DELETE /tasks/{id}` returns `204`.
- `DELETE /tasks/{id}` for an unknown id returns `404`.

Built a minimal frontend that can:

- Show the task list
- Add a task
- Toggle completion

Added my own tests(I listed them in the PR's):

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

Updated the frontend with:

- A priority select when creating or editing tasks
- A priority filter

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
