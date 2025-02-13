import sys
import os
import pytest
from fastapi.testclient import TestClient

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.main import app

client = TestClient(app)

# Фикстура для создания тестового пользователя
@pytest.fixture
def test_user():
    user_data = {"username": "testuser", "password": "testpassword", "role": "User"}
    response = client.post("/users/", json=user_data)
    return response.json()

# Фикстура для получения JWT токена для тестового пользователя
@pytest.fixture
def token(test_user):
    response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    return response.json()["access_token"]

# Тест для проверки создания заметки
def test_create_note(token):
    headers = {"Authorization": f"Bearer {token}"}
    note_data = {"title": "Test Note", "body": "This is a test note."}
    response = client.post("/notes/", json=note_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["body"] == "This is a test note."