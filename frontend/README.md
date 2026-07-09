# Frontend

Plain HTML, CSS, and JavaScript. No build step, no dependencies, no framework.

## Run it

The frontend talks to the backend over HTTP, so start the API first.

Terminal 1 — the API on port 8000:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Terminal 2 — serve these static files on port 5173:

```bash
cd frontend
python3 -m http.server 5173
```

Then open <http://localhost:5173>.

The API base URL is the `API_BASE` constant at the top of `app.js`. The backend
enables permissive CORS for local development, so the two ports can talk.

Opening `index.html` directly with `file://` also works, because the `null`
origin is allowed by that same CORS policy.

## What it does

- Lists tasks, adds a task, toggles completion, and deletes a task.
- Shows an error banner if the API is unreachable.

Task titles are rendered with `textContent`, never `innerHTML`, so a title like
`<img onerror=...>` is displayed as text rather than executed.
