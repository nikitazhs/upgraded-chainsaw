from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    """
    Модель пользователя (таблица 'users').

    Атрибуты:
        id: Уникальный идентификатор пользователя.
        username: Уникальное имя пользователя.
        hashed_password: Хэшированный пароль.
        role: Роль пользователя (например, "User" или "Admin").
        notes: Список заметок, принадлежащих пользователю.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Ограничиваем длину username до 150 символов для оптимизации хранения
    username = Column(String(150), unique=True, index=True, nullable=False)
    # Рекомендуется задать ограничение длины для хэшированного пароля (например, 128 символов)
    hashed_password = Column(String(128), nullable=False)
    # Ограничиваем длину поля role для экономии места
    role = Column(String(50), default="User", nullable=False)

    # Связь "один ко многим": пользователь может иметь несколько заметок.
    # Каскадное удаление гарантирует, что заметки пользователя удаляются вместе с ним.
    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Note(Base):
    """
    Модель заметки (таблица 'notes').

    Атрибуты:
        id: Уникальный идентификатор заметки.
        title: Заголовок заметки.
        body: Текст заметки.
        owner_id: Внешний ключ, указывающий на пользователя, создавшего заметку.
        is_deleted: Флаг мягкого удаления заметки.
        created_at: Дата и время создания заметки.
        updated_at: Дата и время последнего обновления заметки.
        owner: Объект пользователя, владеющий заметкой.
    """
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    body = Column(String(65536), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Обратная связь: каждая заметка принадлежит конкретному пользователю.
    owner = relationship("User", back_populates="notes")

    def __repr__(self) -> str:
        # Ограничиваем длину заголовка для вывода, чтобы не перегружать консоль
        title_preview = self.title if len(self.title) <= 20 else self.title[:17] + "..."
        return f"<Note(id={self.id}, title='{title_preview}', owner_id={self.owner_id}, is_deleted={self.is_deleted})>"
