from pydantic import BaseModel, constr
from typing import Optional
from datetime import datetime

# ---- Схемы для пользователей ----

# Базовая схема пользователя, содержащая только имя.
class UserBase(BaseModel):
    username: str

# Схема для регистрации нового пользователя.
class UserCreate(UserBase):
    password: str
    role: Optional[str] = "User"  # По умолчанию роль "User"

# Схема для возврата данных пользователя (без пароля).
class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True  # Позволяет автоматически преобразовывать объекты SQLAlchemy

# ---- Схемы для заметок ----

# Базовая схема заметки с ограничениями на длину заголовка и текста.
class NoteBase(BaseModel):
    title: constr(max_length=256)
    body: constr(max_length=65536)

# Схема для создания заметки.
class NoteCreate(NoteBase):
    pass

# Схема для обновления заметки. Поля опциональные, чтобы можно было обновлять часть данных.
class NoteUpdate(BaseModel):
    title: Optional[constr(max_length=256)]
    body: Optional[constr(max_length=65536)]

# Схема для возврата данных заметки через API.
class NoteResponse(NoteBase):
    id: int
    owner_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True