# Notes API

Это API для управления заметками, разработанное на FastAPI.

## Функциональность

- **Авторизация и регистрация пользователей:** поддержка ролей "User" и "Admin".
- **Пользователь с ролью "User":**
  - Создает заметку.
  - Изменяет свою заметку.
  - Удаляет свою заметку.
  - Получает список своих заметок.
  - Получает конкретную заметку.
- **Пользователь с ролью "Admin":**
  - Получает список всех заметок.
  - Получает список заметок конкретного пользователя.
  - Восстанавливает удаленные заметки.
- **Логирование:** все действия логируются в файл `app.log`.
- **Юнит-тесты:** тесты написаны с использованием `pytest`.
- **Контейнеризация:** проект можно запустить через Docker.

## Структура проекта
notes-api/ 
        │ 
            ├── app/ │ 
            ├── init.py │ 
            ├── config.py │ 
            ├── database.py │ 
            ├── models.py │ 
            ├── schemas.py │ 
            ├── crud.py │ 
            ├── auth.py │ 
        ├── dependencies.py │ 
        └── main.py │ 
        ├── tests/ │ 
        └── test_main.py │ 
        ├── Dockerfile 
        ├── requirements.txt 
        └── README.md

## Запуск проекта

### Локально

1. **Клонировать репозиторий:**
    ```bash
    git clone https://github.com/nikitazhs/upgraded-chainsaw.git
    cd notes-api
    ```

2. **Создать виртуальное окружение и установить зависимости:**
    ```bash
    python3 -m venv venv
    # Для Linux/Mac:
    source venv/bin/activate
    # Для Windows:
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Запустить приложение:**
    ```bash
    uvicorn app.main:app --reload
    ```

4. **Доступ к API:**
    Откройте браузер и перейдите по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)

### С использованием Docker

1. **Собрать Docker образ:**
    ```bash
    docker build -t notes-api .
    ```

2. **Запустить контейнер:**
    ```bash
    docker run -d --name notes-api -p 8000:8000 notes-api
    ```

3. **Доступ к API:**
    Откройте браузер и перейдите по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)

## Запуск тестов

Для запуска тестов выполните:
```bash
pytest




