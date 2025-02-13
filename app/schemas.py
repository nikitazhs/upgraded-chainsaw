from pydantic import BaseModel, constr, Field
from typing import Optional
from datetime import datetime


# ---- Схемы для пользователей ----

class UserBase(BaseModel):
    """
    Базовая схема пользователя, содержащая только имя.
    """
    username: str = Field(..., title="Username", max_length=150, description="Уникальное имя пользователя")


class UserCreate(UserBase):
    """
    Схема для регистрации нового пользователя.

    Включает пароль и роль, по умолчанию роль 'User'.
    """
    password: str = Field(..., title="Password", min_length=8, description="Пароль пользователя")
    role: Optional[str] = Field("User", title="Role", description="Роль пользователя, по умолчанию 'User'")


class UserResponse(UserBase):
    """
    Схема для возврата данных пользователя (без пароля).
    """
    id: int = Field(..., title="User ID", description="Уникальный идентификатор пользователя")
    role: str = Field(..., title="Role", description="Роль пользователя")

    class Config:
        orm_mode = True  # Позволяет автоматически преобразовывать объекты SQLAlchemy


# ---- Схемы для заметок ----

class NoteBase(BaseModel):
    """
    Базовая схема заметки с ограничениями на длину заголовка и текста.
    """
    title: constr(max_length=256) = Field(..., title="Title", description="Заголовок заметки")
    body: constr(max_length=65536) = Field(..., title="Body", description="Содержимое заметки")


class NoteCreate(NoteBase):
    """
    Схема для создания заметки.

    Наследует все поля из NoteBase.
    """
    pass


class NoteUpdate(BaseModel):
    """
    Схема для обновления заметки.

    Поля опциональные, чтобы можно было обновлять только изменившиеся данные.
    """
    title: Optional[constr(max_length=256)] = Field(None, title="Title", description="Новый заголовок заметки")
    body: Optional[constr(max_length=65536)] = Field(None, title="Body", description="Новый текст заметки")


class NoteResponse(NoteBase):
    """
    Схема для возврата данных заметки через API.
    """
    id: int = Field(..., title="Note ID", description="Уникальный идентификатор заметки")
    owner_id: int = Field(..., title="Owner ID", description="Идентификатор пользователя, создавшего заметку")
    is_deleted: bool = Field(..., title="Is Deleted", description="Флаг мягкого удаления заметки")
    created_at: datetime = Field(..., title="Created At", description="Дата и время создания заметки")
    updated_at: datetime = Field(..., title="Updated At", description="Дата и время последнего обновления заметки")

    class Config:
        orm_mode = True
