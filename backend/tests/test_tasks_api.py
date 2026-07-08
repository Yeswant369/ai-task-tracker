"""Integration tests driving the API through HTTP."""

import pytest


def test_task_lifecycle_create_list_update_delete(client):
    created = client.post("/tasks", json={"title": "buy milk"})
    assert created.status_code == 201
    assert created.json() == {
        "id": 1,
        "title": "buy milk",
        "completed": False,
        "priority": "medium",
    }

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert listed.json() == [
        {"id": 1, "title": "buy milk", "completed": False, "priority": "medium"}
    ]

    toggled = client.patch("/tasks/1", json={"completed": True})
    assert toggled.status_code == 200
    assert toggled.json() == {
        "id": 1,
        "title": "buy milk",
        "completed": True,
        "priority": "medium",
    }

    deleted = client.delete("/tasks/1")
    assert deleted.status_code == 204
    assert deleted.content == b""

    assert client.get("/tasks").json() == []


def test_list_tasks_starts_empty(client):
    assert client.get("/tasks").json() == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": ""},
        {"title": "   "},
        {"title": None},
    ],
    ids=["missing", "empty", "whitespace", "null"],
)
def test_create_task_rejects_invalid_title(client, payload):
    assert client.post("/tasks", json=payload).status_code == 422


def test_create_task_strips_surrounding_whitespace(client):
    response = client.post("/tasks", json={"title": "  padded  "})

    assert response.status_code == 201
    assert response.json()["title"] == "padded"


def test_patch_updates_title_and_completed_together(client):
    client.post("/tasks", json={"title": "draft"})

    response = client.patch("/tasks/1", json={"title": "final", "completed": True})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "final",
        "completed": True,
        "priority": "medium",
    }


def test_patch_with_empty_body_leaves_task_untouched(client):
    client.post("/tasks", json={"title": "unchanged"})

    response = client.patch("/tasks/1", json={})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "unchanged",
        "completed": False,
        "priority": "medium",
    }


def test_patch_rejects_blank_title(client):
    client.post("/tasks", json={"title": "keep me"})

    assert client.patch("/tasks/1", json={"title": "  "}).status_code == 422
    assert client.get("/tasks").json()[0]["title"] == "keep me"


def test_patch_unknown_id_returns_404(client):
    assert client.patch("/tasks/999", json={"completed": True}).status_code == 404


def test_delete_unknown_id_returns_404(client):
    assert client.delete("/tasks/999").status_code == 404


def test_delete_is_not_idempotent_second_call_is_404(client):
    client.post("/tasks", json={"title": "temp"})

    assert client.delete("/tasks/1").status_code == 204
    assert client.delete("/tasks/1").status_code == 404


def test_tasks_are_listed_in_creation_order(client):
    for title in ["first", "second", "third"]:
        client.post("/tasks", json={"title": title})

    assert [task["title"] for task in client.get("/tasks").json()] == [
        "first",
        "second",
        "third",
    ]
