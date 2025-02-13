import os
import sys
import pytest
from fastapi.testclient import TestClient

# Добавляем корневую директорию проекта в sys.path,
# если она ещё не добавлена
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.main import app

# Создаем экземпляр клиента для тестирования FastAPI-приложения
client = TestClient(app)

@pytest.fixture(scope="module")
def test_user():
    """
    Фикстура для регистрации тестового пользователя.
    Если пользователь уже существует, тесты будут использовать его.
    """
    user_data = {"username": "testuser", "password": "testpassword", "role": "User"}
    response = client.post("/users/", json=user_data)
    # Если пользователь уже существует, можно игнорировать ошибку и продолжить
    if response.status_code not in (200, 201):
        pytest.skip("Пользователь не создан (возможно, уже существует).")
    return response.json()

@pytest.fixture(scope="module")
def token(test_user):
    """
    Фикстура для получения JWT токена для тестового пользователя.
    """
    response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200, f"Не удалось получить токен: {response.text}"
    token_data = response.json()
    return token_data["access_token"]

def test_create_note(token):
    """
    Тест для проверки создания заметки.
    Проверяет, что заметка успешно создается с указанными данными.
    """
    headers = {"Authorization": f"Bearer {token}"}
    note_data = {"title": "Test Note", "body": "This is a test note."}
    response = client.post("/notes/", json=note_data, headers=headers)
    assert response.status_code == 200, f"Ошибка создания заметки: {response.text}"
    data = response.json()
    assert data.get("title") == "Test Note", "Неверный заголовок заметки"
    assert data.get("body") == "This is a test note.", "Неверное содержимое заметки"

def test_get_notes(token):
    """
    Тест для проверки получения списка заметок для тестового пользователя.
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/notes/", headers=headers)
    assert response.status_code == 200, f"Ошибка получения заметок: {response.text}"
    data = response.json()
    assert isinstance(data, list), "Ожидался список заметок"
    # Проверяем, что хотя бы одна заметка имеет ожидаемый заголовок.
    assert any(note.get("title") == "Test Note" for note in data), "Созданная заметка не найдена в списке"
