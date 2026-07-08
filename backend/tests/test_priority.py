"""Tests for PR 2 priority support, plus regression cover for PR 1 behaviour."""

import pytest

from app.storage import TaskStorage


def titles(response) -> list[str]:
    return [task["title"] for task in response.json()]


# --- Regression: PR 1 behaviour must survive the priority change -------------


def test_regression_create_without_priority_still_works(client):
    """PR 1 clients never send priority. They must keep getting a 201."""
    response = client.post("/tasks", json={"title": "legacy client"})

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "legacy client",
        "completed": False,
        "priority": "medium",
    }


def test_regression_pr1_status_codes_are_unchanged(client):
    assert client.post("/tasks", json={"title": ""}).status_code == 422
    assert client.post("/tasks", json={}).status_code == 422
    assert client.patch("/tasks/999", json={"completed": True}).status_code == 404
    assert client.delete("/tasks/999").status_code == 404

    client.post("/tasks", json={"title": "temp"})
    assert client.delete("/tasks/1").status_code == 204


def test_regression_unfiltered_list_returns_creation_order(client):
    """No query params must behave exactly as it did in PR 1."""
    for title in ["first", "second", "third"]:
        client.post("/tasks", json={"title": title, "priority": "low"})
    client.post("/tasks", json={"title": "fourth", "priority": "high"})

    assert titles(client.get("/tasks")) == ["first", "second", "third", "fourth"]


def test_regression_patch_without_priority_preserves_existing_priority(client):
    client.post("/tasks", json={"title": "keep", "priority": "high"})

    response = client.patch("/tasks/1", json={"completed": True})

    assert response.json()["priority"] == "high"


# --- Priority on create and update -------------------------------------------


@pytest.mark.parametrize("priority", ["low", "medium", "high"])
def test_create_accepts_each_valid_priority(client, priority):
    response = client.post("/tasks", json={"title": "task", "priority": priority})

    assert response.status_code == 201
    assert response.json()["priority"] == priority


@pytest.mark.parametrize("priority", ["urgent", "HIGH", "", 1, None])
def test_create_rejects_invalid_priority(client, priority):
    response = client.post("/tasks", json={"title": "task", "priority": priority})

    assert response.status_code == 422


def test_patch_updates_priority(client):
    client.post("/tasks", json={"title": "task"})

    response = client.patch("/tasks/1", json={"priority": "high"})

    assert response.status_code == 200
    assert response.json()["priority"] == "high"


def test_patch_rejects_invalid_priority_and_leaves_task_untouched(client):
    client.post("/tasks", json={"title": "task", "priority": "low"})

    assert client.patch("/tasks/1", json={"priority": "urgent"}).status_code == 422
    assert client.get("/tasks").json()[0]["priority"] == "low"


# --- Filtering ---------------------------------------------------------------


def test_filter_by_priority(client):
    client.post("/tasks", json={"title": "a", "priority": "high"})
    client.post("/tasks", json={"title": "b", "priority": "low"})
    client.post("/tasks", json={"title": "c", "priority": "high"})

    assert titles(client.get("/tasks?priority=high")) == ["a", "c"]
    assert titles(client.get("/tasks?priority=low")) == ["b"]
    assert titles(client.get("/tasks?priority=medium")) == []


def test_filter_by_invalid_priority_returns_422(client):
    assert client.get("/tasks?priority=urgent").status_code == 422


# --- Sorting -----------------------------------------------------------------


def test_sort_by_priority_orders_high_medium_low(client):
    client.post("/tasks", json={"title": "low one", "priority": "low"})
    client.post("/tasks", json={"title": "high one", "priority": "high"})
    client.post("/tasks", json={"title": "medium one", "priority": "medium"})

    assert titles(client.get("/tasks?sort=priority")) == [
        "high one",
        "medium one",
        "low one",
    ]


def test_sort_is_stable_within_a_priority(client):
    """Equal priorities must keep creation order, not an arbitrary one."""
    client.post("/tasks", json={"title": "low first", "priority": "low"})
    client.post("/tasks", json={"title": "high first", "priority": "high"})
    client.post("/tasks", json={"title": "high second", "priority": "high"})
    client.post("/tasks", json={"title": "low second", "priority": "low"})

    assert titles(client.get("/tasks?sort=priority")) == [
        "high first",
        "high second",
        "low first",
        "low second",
    ]


def test_sort_by_unknown_field_returns_422(client):
    assert client.get("/tasks?sort=title").status_code == 422


def test_filter_and_sort_combine(client):
    client.post("/tasks", json={"title": "b high", "priority": "high"})
    client.post("/tasks", json={"title": "a low", "priority": "low"})
    client.post("/tasks", json={"title": "a high", "priority": "high"})

    assert titles(client.get("/tasks?priority=high&sort=priority")) == [
        "b high",
        "a high",
    ]


# --- Storage unit tests -------------------------------------------------------


def test_storage_filter_does_not_mutate_stored_order():
    store = TaskStorage()
    store.create_task("low", "low")
    store.create_task("high", "high")

    store.list_tasks(sort="priority")

    # Sorting a returned copy must not reorder the underlying store.
    assert [task["title"] for task in store.list_tasks()] == ["low", "high"]


def test_storage_create_defaults_to_medium():
    store = TaskStorage()

    assert store.create_task("no priority given")["priority"] == "medium"
