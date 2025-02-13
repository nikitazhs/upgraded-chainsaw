"""
Модуль для настройки подключения к базе данных с использованием SQLAlchemy.

Данный модуль:
- Получает URL подключения из переменной окружения DATABASE_URL (по умолчанию используется SQLite).
- Создает объект engine для подключения к базе данных.
- Настраивает фабрику сессий SessionLocal для создания сессий.
- Определяет базовый класс Base для всех моделей SQLAlchemy.

Использование:
    from .database import SessionLocal, Base, engine
    # Получить сессию:
    db = SessionLocal()
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Получаем URL подключения из переменной окружения или используем SQLite по умолчанию
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./notes.db")

# Для SQLite используем параметр connect_args, чтобы отключить проверку потоков
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}

# Создаем объект engine с параметром future=True для использования нового API SQLAlchemy 2.0
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    future=True
)

# Создаем SessionLocal - фабрику сессий с использованием нового API
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Определяем базовый класс для моделей
Base = declarative_base()
