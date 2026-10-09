"""Tests for the /admin endpoints."""


def test_admin_list_users(client, admin_headers, user):
    response = client.get("/admin/users", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["id"] == user["id"] for item in data)


def test_admin_endpoints_require_admin(client, headers, user):
    list_response = client.get("/admin/users", headers=headers)

    assert list_response.status_code == 403
    assert list_response.json()["detail"] == "Admin access required"

    delete_response = client.delete(
        "/admin/users/{}".format(user["id"]), headers=headers
    )

    assert delete_response.status_code == 403
    assert delete_response.json()["detail"] == "Admin access required"
