# Agent Instructions

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

```bash
cd backend
uvicorn app.main:app --reload
```

## Test

```bash
cd backend
pytest
pytest -m pr1
pytest -m pr2
```

## Commit Template

```bash
git config commit.template .gitmessage
```

Used the prefilled `.gitmessage` when committing assessment work. Kept the AI usage section specific and meaningful.

## Rules

- Never modify files under `backend/tests/acceptance/`.
- Never modify `backend/pytest.ini`.
- Never modify `.github/workflows/ci.yml`.
- Implemented the backend work in `backend/app/` and frontend work in `frontend/`.

