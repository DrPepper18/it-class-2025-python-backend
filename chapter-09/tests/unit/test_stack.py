import os

import pytest
from fastapi.testclient import TestClient

from app.app import app


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """
    Простая фикстура, чтобы в тестовой среде всегда был SECRET_TOKEN.
    В реальном проекте его берут из .env, здесь — для удобства.
    """
    os.environ.setdefault("SECRET_TOKEN", "test-secret-key")


@pytest.fixture
def client():
    return TestClient(app)


def register_and_login(client: TestClient, username: str = "test_user", password: str = "password123") -> str:
    """
    Вспомогательная функция: регистрирует пользователя и возвращает JWT-токен.
    Используется в нескольких тестах.
    """
    # Регистрация
    resp = client.post(
        "/users/register",
        json={"username": username, "password": password},
    )
    # Если пользователь уже есть — это не критично для теста
    assert resp.status_code in (200, 400)

    # Логин
    resp = client.post(
        "/users/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    return data["access_token"]


def test_stack_size_initial_is_zero(client: TestClient):
    """
    Простой "юнит"-тест уровня API:
    после авторизации размер стека для нового пользователя должен быть 0.
    """
    token = register_and_login(client, username="unit_user_1")

    resp = client.get(
        "/stack/size",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["stack_size"] == 0
    assert data["is_empty"] is True


def test_push_increases_size(client: TestClient):
    """
    Проверяем, что push увеличивает размер стека на 1.
    """
    token = register_and_login(client, username="unit_user_2")

    # Был пустой
    resp = client.get(
        "/stack/size",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    initial_size = resp.json()["stack_size"]

    # Делаем push
    resp = client.post(
        "/stack/push",
        json={"value": 42},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    # Размер должен увеличиться
    resp = client.get(
        "/stack/size",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    new_size = resp.json()["stack_size"]

    assert new_size == initial_size + 1


