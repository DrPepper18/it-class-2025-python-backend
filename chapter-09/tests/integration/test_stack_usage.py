import os

import pytest
from fastapi.testclient import TestClient

from app.app import app


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    os.environ.setdefault("SECRET_TOKEN", "test-secret-key")


@pytest.fixture
def client():
    return TestClient(app)


def register_and_login(client: TestClient, username: str = "integration_user", password: str = "password123") -> str:
    resp = client.post(
        "/users/register",
        json={"username": username, "password": password},
    )
    assert resp.status_code in (200, 400)

    resp = client.post(
        "/users/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_full_stack_usage_for_single_user(client: TestClient):
    """
    Интеграционный сценарий:
    - пользователь логинится
    - пушит несколько значений
    - проверяет размер
    - делает pop
    - чистит стек
    """
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Стек пуст
    resp = client.get("/stack/size", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["stack_size"] == 0

    # Push 3 значений
    for value in (10, 20, 30):
        resp = client.post("/stack/push", json={"value": value}, headers=headers)
        assert resp.status_code == 200

    # Размер должен быть 3
    resp = client.get("/stack/size", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["stack_size"] == 3
    assert data["is_empty"] is False

    # Pop возвращает последнее значение (30)
    resp = client.get("/stack/pop", headers=headers)
    assert resp.status_code == 200
    assert "30" in resp.json()["message"]

    # Очистка стека
    resp = client.delete("/stack/clear", headers=headers)
    assert resp.status_code == 200

    # После очистки стек пуст
    resp = client.get("/stack/size", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["stack_size"] == 0
    assert resp.json()["is_empty"] is True


