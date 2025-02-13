from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

# Модель пользователя (таблица users)
class User(Base):
    __tablename__ = "users"  # Название таблицы

    # Уникальный идентификатор пользователя
    id = Column(Integer, primary_key=True, index=True)
    # Имя пользователя. Должно быть уникальным.
    username = Column(String, unique=True, index=True, nullable=False)
    # Хэшированный пароль пользователя
    hashed_password = Column(String, nullable=False)
    # Роль пользователя: "User" или "Admin". По умолчанию "User".
    role = Column(String, default="User")
    # Определяем связь "один ко многим": пользователь может иметь несколько заметок.
    notes = relationship("Note", back_populates="owner")

# Модель заметки (таблица notes)
class Note(Base):
    __tablename__ = "notes"  # Название таблицы

    # Уникальный идентификатор заметки
    id = Column(Integer, primary_key=True, index=True)
    # Заголовок заметки (ограничение в 256 символов накладывается через Pydantic-схему)
    title = Column(String(256), nullable=False)
    # Текст заметки (ограничение в 65536 символов накладывается через Pydantic-схему)
    body = Column(String(65536), nullable=False)
    # Внешний ключ, ссылающийся на пользователя, создавшего заметку
    owner_id = Column(Integer, ForeignKey("users.id"))
    # Флаг мягкого удаления: если True, заметка считается удалённой.
    is_deleted = Column(Boolean, default=False)
    # Дата создания заметки. По умолчанию — текущее время.
    created_at = Column(DateTime, default=datetime.utcnow)
    # Дата последнего обновления заметки. Автоматически обновляется при изменении.
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Обратная связь: заметка принадлежит конкретному пользователю.
    owner = relationship("User", back_populates="notes")