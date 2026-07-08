from typing import Any


class TaskStorage:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._tasks: dict[int, dict[str, Any]] = {}
        self._next_id = 1

    def create_task(self, title: str) -> dict[str, Any]:
        task: dict[str, Any] = {
            "id": self._next_id,
            "title": title,
            "completed": False,
        }
        self._tasks[self._next_id] = task
        self._next_id += 1
        return dict(task)

    def list_tasks(self) -> list[dict[str, Any]]:
        # dicts preserve insertion order, so tasks come back oldest-first.
        return [dict(task) for task in self._tasks.values()]

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        task = self._tasks.get(task_id)
        return dict(task) if task is not None else None

    def update_task(
        self,
        task_id: int,
        *,
        title: str | None = None,
        completed: bool | None = None,
    ) -> dict[str, Any] | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None

        if title is not None:
            task["title"] = title
        if completed is not None:
            task["completed"] = completed

        return dict(task)

    def delete_task(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None


storage = TaskStorage()
