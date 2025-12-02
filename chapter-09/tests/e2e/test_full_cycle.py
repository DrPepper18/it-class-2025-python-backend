import os
import uuid

import pytest
from fastapi.testclient import TestClient

from app.app import app


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    os.environ.setdefault("SECRET_TOKEN", "test-secret-key")


@pytest.fixture
def client():
    return TestClient(app)


def test_full_cycle_happy_path(client: TestClient):
    """
    E2E-сценарий "счастливого пути":
    - новый пользователь регистрируется
    - логинится и получает токен
    - работает со стеком (push / size / pop / clear)
    """
    username = f"e2e_user_{uuid.uuid4().hex[:8]}"
    password = "e2e_password"

    # Регистрация
    resp = client.post(
        "/users/register",
        json={"username": username, "password": password},
    )
    assert resp.status_code in (200, 400)

    # Логин
    resp = client.post(
        "/users/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Работа со стеком
    resp = client.get("/stack/size", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["stack_size"] == 0

    resp = client.post("/stack/push", json={"value": 100}, headers=headers)
    assert resp.status_code == 200

    resp = client.get("/stack/size", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["stack_size"] == 1

    resp = client.get("/stack/pop", headers=headers)
    assert resp.status_code == 200
    assert "100" in resp.json()["message"]

    resp = client.delete("/stack/clear", headers=headers)
    assert resp.status_code == 200


def test_access_denied_without_token(client: TestClient):
    """
    E2E-сценарий ошибки:
    попытка обратиться к защищённым эндпоинтам без токена должна давать 403/401.
    """
    resp = client.get("/stack/size")
    assert resp.status_code in (401, 403)

    resp = client.post("/stack/push", json={"value": 1})
    assert resp.status_code in (401, 403)

    resp = client.get("/stack/pop")
    assert resp.status_code in (401, 403)


