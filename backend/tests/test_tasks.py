"""Tests for the /tasks endpoints."""


def create_project(client, headers, name="Task parent"):
    response = client.post(
        "/projects/", json={"name": name, "description": None}, headers=headers
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_create_task(client, headers, user):
    project_id = create_project(client, headers)

    response = client.post(
        "/tasks/",
        json={"name": "Write the report", "project_id": project_id},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["name"] == "Write the report"
    assert data["is_completed"] is False
    assert data["project_id"] == project_id
    assert data["owner_id"] == user["id"]


def test_create_task_rejects_unknown_project(client, headers):
    response = client.post(
        "/tasks/", json={"name": "Orphan", "project_id": 999999}, headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_create_task_rejects_empty_name(client, headers):
    project_id = create_project(client, headers)

    response = client.post(
        "/tasks/", json={"name": "   ", "project_id": project_id}, headers=headers
    )

    assert response.status_code == 422


def test_list_tasks_returns_only_my_tasks(client, headers, user, new_user, login):
    project_id = create_project(client, headers, "My tasks")
    mine = []
    for name in ("First", "Second"):
        created = client.post(
            "/tasks/", json={"name": name, "project_id": project_id}, headers=headers
        )
        assert created.status_code == 200
        mine.append(created.json()["id"])

    other = new_user(prefix="other-owner")
    other_headers = {"Authorization": "Bearer " + login(other)}
    other_project = create_project(client, other_headers, "Their tasks")
    foreign = client.post(
        "/tasks/",
        json={"name": "Theirs", "project_id": other_project},
        headers=other_headers,
    )
    assert foreign.status_code == 200
    foreign_id = foreign.json()["id"]

    response = client.get("/tasks/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    ids = [item["id"] for item in data]
    for task_id in mine:
        assert task_id in ids
    assert foreign_id not in ids
    for item in data:
        assert item["owner_id"] == user["id"]


def test_get_task_by_id(client, headers):
    project_id = create_project(client, headers)
    created = client.post(
        "/tasks/", json={"name": "Fetchable", "project_id": project_id}, headers=headers
    ).json()

    response = client.get("/tasks/{}".format(created["id"]), headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["name"] == "Fetchable"
    assert data["project_id"] == project_id
    assert data["is_completed"] is False


def test_get_missing_task_returns_404(client, headers):
    response = client.get("/tasks/999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "task not found"


def test_cannot_read_another_users_task(client, headers, new_user, login):
    project_id = create_project(client, headers)
    mine = client.post(
        "/tasks/", json={"name": "Private", "project_id": project_id}, headers=headers
    ).json()

    stranger = new_user(prefix="stranger")
    stranger_headers = {"Authorization": "Bearer " + login(stranger)}

    response = client.get("/tasks/{}".format(mine["id"]), headers=stranger_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "task not found"


def test_update_task(client, headers):
    project_id = create_project(client, headers)
    created = client.post(
        "/tasks/", json={"name": "Old name", "project_id": project_id}, headers=headers
    ).json()

    response = client.put(
        "/tasks/{}".format(created["id"]),
        json={"name": "New name", "is_completed": True},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["name"] == "New name"
    assert data["is_completed"] is True
    assert data["project_id"] == project_id

    stored = client.get("/tasks/{}".format(created["id"]), headers=headers)
    assert stored.status_code == 200
    assert stored.json()["is_completed"] is True


def test_update_task_rejects_missing_completion_flag(client, headers):
    project_id = create_project(client, headers)
    created = client.post(
        "/tasks/", json={"name": "Half updated", "project_id": project_id}, headers=headers
    ).json()

    response = client.put(
        "/tasks/{}".format(created["id"]), json={"name": "Half updated"}, headers=headers
    )

    assert response.status_code == 422


def test_update_missing_task_returns_404(client, headers):
    response = client.put(
        "/tasks/999999",
        json={"name": "Ghost", "is_completed": False},
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "task not found"


def test_delete_task(client, headers):
    project_id = create_project(client, headers)
    created = client.post(
        "/tasks/", json={"name": "Disposable", "project_id": project_id}, headers=headers
    ).json()

    response = client.delete("/tasks/{}".format(created["id"]), headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted Successfully"

    follow_up = client.get("/tasks/{}".format(created["id"]), headers=headers)
    assert follow_up.status_code == 404


def test_delete_missing_task_returns_404(client, headers):
    response = client.delete("/tasks/999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "task not found"


def test_tasks_require_authentication(client):
    assert client.get("/tasks/").status_code == 401
    assert client.post("/tasks/", json={"name": "Anonymous", "project_id": 1}).status_code == 401
    assert client.get("/tasks/1").status_code == 401
    assert client.put("/tasks/1", json={"name": "Anonymous", "is_completed": False}).status_code == 401
    assert client.delete("/tasks/1").status_code == 401
