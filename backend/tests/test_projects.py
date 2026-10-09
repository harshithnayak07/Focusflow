"""Tests for the /projects endpoints."""


def test_create_project(client, headers, user):
    payload = {"name": "Landing page", "description": "Redesign the landing page"}

    response = client.post("/projects/", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["name"] == "Landing page"
    assert data["description"] == "Redesign the landing page"
    assert data["owner_id"] == user["id"]


def test_create_project_allows_missing_description(client, headers):
    response = client.post(
        "/projects/", json={"name": "No description"}, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["description"] is None


def test_create_project_rejects_empty_name(client, headers):
    response = client.post("/projects/", json={"name": "   "}, headers=headers)

    assert response.status_code == 422


def test_list_projects_returns_only_my_projects(client, headers, user, new_user, login):
    mine = []
    for index in range(2):
        created = client.post(
            "/projects/",
            json={"name": "Mine {}".format(index), "description": None},
            headers=headers,
        )
        assert created.status_code == 200
        mine.append(created.json()["id"])

    other = new_user(prefix="other-owner")
    other_headers = {"Authorization": "Bearer " + login(other)}
    foreign = client.post(
        "/projects/",
        json={"name": "Not mine", "description": None},
        headers=other_headers,
    )
    assert foreign.status_code == 200
    foreign_id = foreign.json()["id"]

    response = client.get("/projects/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    ids = [item["id"] for item in data]
    for project_id in mine:
        assert project_id in ids
    assert foreign_id not in ids
    for item in data:
        assert item["owner_id"] == user["id"]


def test_get_project_by_id(client, headers, user):
    created = client.post(
        "/projects/",
        json={"name": "Fetchable", "description": "Read me"},
        headers=headers,
    ).json()

    response = client.get("/projects/{}".format(created["id"]), headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["name"] == "Fetchable"
    assert data["description"] == "Read me"
    assert data["owner_id"] == user["id"]


def test_get_missing_project_returns_404(client, headers):
    response = client.get("/projects/999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_cannot_read_another_users_project(client, headers, new_user, login):
    foreign = client.post(
        "/projects/",
        json={"name": "Private", "description": None},
        headers=headers,
    ).json()

    stranger = new_user(prefix="stranger")
    stranger_headers = {"Authorization": "Bearer " + login(stranger)}

    response = client.get("/projects/{}".format(foreign["id"]), headers=stranger_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_update_project(client, headers):
    created = client.post(
        "/projects/",
        json={"name": "Old name", "description": "Old description"},
        headers=headers,
    ).json()

    response = client.put(
        "/projects/{}".format(created["id"]),
        json={"name": "New name", "description": "New description"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["name"] == "New name"
    assert data["description"] == "New description"

    stored = client.get("/projects/{}".format(created["id"]), headers=headers)
    assert stored.status_code == 200
    assert stored.json()["name"] == "New name"


def test_update_missing_project_returns_404(client, headers):
    response = client.put(
        "/projects/999999",
        json={"name": "Ghost", "description": None},
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_delete_project(client, headers):
    created = client.post(
        "/projects/",
        json={"name": "Temporary", "description": None},
        headers=headers,
    ).json()

    response = client.delete("/projects/{}".format(created["id"]), headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "project deleted Successfully"

    follow_up = client.get("/projects/{}".format(created["id"]), headers=headers)
    assert follow_up.status_code == 404


def test_delete_missing_project_returns_404(client, headers):
    response = client.delete("/projects/999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_projects_require_authentication(client):
    assert client.get("/projects/").status_code == 401
    assert client.post("/projects/", json={"name": "Anonymous"}).status_code == 401
    assert client.get("/projects/1").status_code == 401
    assert client.put("/projects/1", json={"name": "Anonymous"}).status_code == 401
    assert client.delete("/projects/1").status_code == 401
