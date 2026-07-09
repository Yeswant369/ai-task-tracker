"""Unit tests for the in-memory storage layer."""

import pytest

from app.models import TaskCreate, clean_title
from app.storage import TaskStorage


@pytest.fixture
def store() -> TaskStorage:
    return TaskStorage()


def test_create_task_assigns_incrementing_ids_and_defaults_to_incomplete(store):
    first = store.create_task("write tests")
    second = store.create_task("read code")

    assert first == {"id": 1, "title": "write tests", "completed": False}
    assert second == {"id": 2, "title": "read code", "completed": False}


def test_ids_are_not_reused_after_delete(store):
    store.create_task("first")
    assert store.delete_task(1) is True

    # A fresh task must not reclaim id 1, or stale client references would
    # silently point at the wrong task.
    assert store.create_task("second")["id"] == 2


def test_update_task_applies_only_provided_fields(store):
    store.create_task("original")

    assert store.update_task(1, completed=True) == {
        "id": 1,
        "title": "original",
        "completed": True,
    }
    # title=None means "not provided", so the title survives.
    assert store.get_task(1)["title"] == "original"

    assert store.update_task(1, title="renamed")["completed"] is True


def test_update_and_delete_return_miss_markers_for_unknown_id(store):
    assert store.update_task(999, title="ghost") is None
    assert store.delete_task(999) is False


def test_list_tasks_returns_copies(store):
    store.create_task("original")

    store.list_tasks()[0]["title"] = "mutated"

    assert store.get_task(1)["title"] == "original"


def test_clean_title_strips_whitespace_and_rejects_blank():
    assert clean_title("  spaced  ") == "spaced"

    with pytest.raises(ValueError):
        clean_title("   ")


def test_task_create_rejects_whitespace_only_title():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        TaskCreate(title="   ")
