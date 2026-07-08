from typing import Any


class TaskStorage:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._tasks: dict[int, dict[str, Any]] = {}
        self._next_id = 1

    def create_task(self, title: str) -> dict[str, Any]:
        raise NotImplementedError

    def list_tasks(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        raise NotImplementedError

    def update_task(
        self,
        task_id: int,
        *,
        title: str | None = None,
        completed: bool | None = None,
    ) -> dict[str, Any] | None:
        raise NotImplementedError

    def delete_task(self, task_id: int) -> bool:
        raise NotImplementedError


storage = TaskStorage()

