"""Shared fixtures for the FocusFlow test suite.

The application is pointed at a throwaway SQLite database before it is
imported, so the suite never reads from or writes to the production
database and can be run repeatedly with identical results.
"""

import os
import shutil
import tempfile
import uuid

_TEST_DB_DIR = tempfile.mkdtemp(prefix="focusflow-tests-")
_TEST_DB_PATH = os.path.join(_TEST_DB_DIR, "focusflow-test.db").replace("\\", "/")
os.environ["DATABASE_URL"] = "sqlite:///" + _TEST_DB_PATH

import pytest
from fastapi.testclient import TestClient


def unique_email(prefix="user"):
    return "{}-{}@example.com".format(prefix, uuid.uuid4().hex[:12])


def auth_headers_for(token):
    return {"Authorization": "Bearer " + token}


@pytest.fixture(scope="session")
def client():
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
def _test_database_cleanup():
    yield
    from app.database.connection import engine

    engine.dispose()
    shutil.rmtree(_TEST_DB_DIR, ignore_errors=True)


@pytest.fixture
def new_user(client):
    def register(prefix="user", name="Test User", password="password-123"):
        payload = {"name": name, "email": unique_email(prefix), "password": password}
        response = client.post("/users/", json=payload)
        assert response.status_code == 200, response.text
        data = response.json()
        data["password"] = password
        return data

    return register


@pytest.fixture
def user(new_user):
    return new_user()


@pytest.fixture
def login(client):
    def authenticate(account):
        response = client.post(
            "/users/login",
            data={"username": account["email"], "password": account["password"]},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["token_type"] == "Bearer"
        assert body["access_token"]
        return body["access_token"]

    return authenticate


@pytest.fixture
def headers(user, login):
    return auth_headers_for(login(user))


@pytest.fixture
def admin_headers(client):
    from app.core.security import hash_password
    from app.database.connection import Sessionlocal
    from app.models.user import User

    db = Sessionlocal()
    try:
        admin = User(
            name="Admin User",
            email=unique_email("admin"),
            password_hash=hash_password("password-123"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    finally:
        db.close()

    response = client.post(
        "/users/login",
        data={"username": admin.email, "password": "password-123"},
    )
    assert response.status_code == 200, response.text
    return auth_headers_for(response.json()["access_token"])
