"""Tests for the /users endpoints."""

import pytest

from conftest import auth_headers_for, unique_email


def test_create_user(client):
    email = unique_email("create")
    payload = {"name": "Ada Lovelace", "email": email, "password": "password-123"}

    response = client.post("/users/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["name"] == "Ada Lovelace"
    assert data["email"] == email
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


def test_create_user_rejects_invalid_email(client):
    payload = {"name": "No Mail", "email": "not-an-email", "password": "password-123"}

    response = client.post("/users/", json=payload)

    assert response.status_code == 422


def test_create_user_rejects_short_password(client):
    payload = {"name": "Short Pw", "email": unique_email("short"), "password": "abc"}

    response = client.post("/users/", json=payload)

    assert response.status_code == 422


def test_create_user_rejects_duplicate_email(client):
    email = unique_email("dup")
    first = client.post(
        "/users/", json={"name": "First", "email": email, "password": "password-123"}
    )
    second = client.post(
        "/users/", json={"name": "Second", "email": email, "password": "password-123"}
    )

    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["detail"] == "Email already registered"


def test_get_all_users(client, user):
    response = client.get("/users/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["id"] == user["id"] for item in data)
    for item in data:
        assert set(item) == {"id", "name", "email", "role", "is_active"}


def test_get_user_by_id(client, user):
    response = client.get("/users/{}".format(user["id"]))

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["name"] == user["name"]
    assert data["email"] == user["email"]
    assert data["role"] == user["role"]


def test_get_missing_user_returns_404(client):
    response = client.get("/users/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_login_returns_token(client, user):
    response = client.post(
        "/users/login",
        data={"username": user["email"], "password": user["password"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "Bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_rejects_wrong_password(client, user):
    response = client.post(
        "/users/login",
        data={"username": user["email"], "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/users/login",
        data={"username": unique_email("ghost"), "password": "password-123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_me_returns_current_user(client, user, login):
    token = login(user)

    response = client.get("/users/me", headers={"Authorization": "Bearer " + token})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["name"] == user["name"]
    assert data["email"] == user["email"]


def test_me_requires_token(client):
    response = client.get("/users/me")

    assert response.status_code == 401



def test_me_rejects_invalid_token(client):
    response = client.get(
        "/users/me", headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401


def test_update_user(client, user):
    response = client.put(
        "/users/{}".format(user["id"]), json={"name": "Updated Name"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["name"] == "Updated Name"
    assert data["email"] == user["email"]

    stored = client.get("/users/{}".format(user["id"]))
    assert stored.status_code == 200
    assert stored.json()["name"] == "Updated Name"


def test_update_missing_user_returns_404(client):
    response = client.put("/users/999999", json={"name": "Ghost"})

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user(client, new_user):
    account = new_user(prefix="delete")

    delete_response = client.delete("/users/{}".format(account["id"]))

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "User deleted Successfully"

    follow_up = client.get("/users/{}".format(account["id"]))
    assert follow_up.status_code == 404
    assert follow_up.json()["detail"] == "User not found"


def test_delete_missing_user_returns_404(client):
    response = client.delete("/users/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def make_account(new_user, login, prefix):
    account = new_user(prefix=prefix)
    return account, auth_headers_for(login(account))


def test_delete_user_with_projects_returns_409(client, new_user, login):
    account, account_headers = make_account(new_user, login, "delete-blocked")
    created = client.post(
        "/projects/", json={"name": "Untouchable", "description": None},
        headers=account_headers,
    )
    assert created.status_code == 200, created.text
    project_id = created.json()["id"]

    response = client.delete("/users/{}".format(account["id"]))

    assert response.status_code == 409
    assert response.json()["detail"] == "User still has projects or tasks"

    assert client.get("/users/{}".format(account["id"])).status_code == 200
    kept = client.get("/projects/{}".format(project_id), headers=account_headers)
    assert kept.status_code == 200
    assert kept.json()["owner_id"] == account["id"]


def test_delete_user_with_tasks_returns_409(client, new_user, login):
    account, account_headers = make_account(new_user, login, "delete-blocked-task")
    project_id = client.post(
        "/projects/", json={"name": "Host", "description": None},
        headers=account_headers,
    ).json()["id"]
    created = client.post(
        "/tasks/", json={"name": "Survivor", "project_id": project_id},
        headers=account_headers,
    )
    assert created.status_code == 200, created.text
    task_id = created.json()["id"]

    response = client.delete("/users/{}".format(account["id"]))

    assert response.status_code == 409
    assert response.json()["detail"] == "User still has projects or tasks"

    assert client.get("/users/{}".format(account["id"])).status_code == 200
    kept = client.get("/tasks/{}".format(task_id), headers=account_headers)
    assert kept.status_code == 200
    assert kept.json()["owner_id"] == account["id"]


def test_delete_user_succeeds_after_content_removed(client, new_user, login):
    account, account_headers = make_account(new_user, login, "delete-cleaned")
    project_id = client.post(
        "/projects/", json={"name": "Temp", "description": None},
        headers=account_headers,
    ).json()["id"]
    task_id = client.post(
        "/tasks/", json={"name": "Temp task", "project_id": project_id},
        headers=account_headers,
    ).json()["id"]

    task_delete = client.delete(
        "/tasks/{}".format(task_id), headers=account_headers
    )
    assert task_delete.status_code == 200, task_delete.text
    project_delete = client.delete(
        "/projects/{}".format(project_id), headers=account_headers
    )
    assert project_delete.status_code == 200, project_delete.text

    response = client.delete("/users/{}".format(account["id"]))

    assert response.status_code == 200
    assert response.json()["message"] == "User deleted Successfully"
    assert client.get("/users/{}".format(account["id"])).status_code == 404
