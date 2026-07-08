from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.models import Priority, Task, TaskCreate, TaskUpdate
from app.storage import storage

app = FastAPI(title="Task Tracker")

# The frontend is served as static files from a separate origin during local
# development. No credentials are involved, so a permissive policy is fine here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> dict:
    return storage.create_task(payload.title, payload.priority.value)


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    # Typing these rejects unknown values with a 422 before the handler runs.
    priority: Priority | None = Query(default=None),
    sort: Literal["priority"] | None = Query(default=None),
) -> list[dict]:
    return storage.list_tasks(
        priority=priority.value if priority is not None else None,
        sort=sort,
    )


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> dict:
    task = storage.update_task(
        task_id,
        title=payload.title,
        completed=payload.completed,
        priority=payload.priority.value if payload.priority is not None else None,
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
