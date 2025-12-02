import os
import pytest
from fastapi.testclient import TestClient

from app.app import app


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    os.environ.setdefault("SECRET_TOKEN", "test-secret-key")


@pytest.fixture(scope="session")
def client():
    return TestClient(app)

def test_register(client: TestClient, username: str = "pytest_user", password: str = "password123") -> str:
    # Регистрация
    resp = client.post(
        "/users/register",
        json={"username": username, "password": password},
    )
    # Если пользователь уже есть — это не критично для теста
    assert resp.status_code in (200, 400)


def test_login(client: TestClient, username: str = "pytest_user", password: str = "password123") -> str:
    # Логин
    resp = client.post(
        "/users/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data