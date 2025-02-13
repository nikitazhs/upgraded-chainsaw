from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging
from datetime import timedelta

from . import models, schemas, crud, auth
from .database import engine, Base
from .dependencies import get_db, get_current_user, require_role
from .config import ACCESS_TOKEN_EXPIRE_MINUTES

# Создаем все таблицы в базе данных, если они еще не существуют
Base.metadata.create_all(bind=engine)

# Настройка логирования: все действия записываются в файл app.log
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Notes API")


# Эндпоинт для авторизации и получения JWT токена
@app.post("/token")
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    # Ищем пользователя по username
    user = crud.get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")

    # Проверяем пароль с использованием passlib
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")

    # Задаем время жизни токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Создаем JWT токен, передавая в него username в качестве идентификатора ("sub")
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logging.info(f"Пользователь {user.username} вошёл в систему.")
    return {"access_token": access_token, "token_type": "bearer"}


# --- Эндпоинт для регистрации нового пользователя ---

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли уже пользователь с таким именем
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    new_user = crud.create_user(db, user)
    logging.info(f"Создан новый пользователь: {new_user.username} с ролью {new_user.role}")
    return new_user


# ------------------- Эндпоинты для пользователей с ролью "User" -------------------

# Создание новой заметки
@app.post("/notes/", response_model=schemas.NoteResponse)
def create_note(
        note: schemas.NoteCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_note = crud.create_note(db, note, current_user.id)
    logging.info(f"Пользователь {current_user.username} с ролью {current_user.role} создал заметку с ID {db_note.id}")
    return db_note


# Получение списка заметок текущего пользователя
@app.get("/notes/", response_model=list[schemas.NoteResponse])
def read_notes(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    notes = crud.get_notes_by_owner(db, current_user.id)
    logging.info(f"Пользователь {current_user.username} запросил список своих заметок")
    return notes


# Получение конкретной заметки по id. Доступ разрешен, если заметка принадлежит текущему пользователю
# или если пользователь имеет роль "Admin"
@app.get("/notes/{note_id}", response_model=schemas.NoteResponse)
def read_note(
        note_id: int,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    note = crud.get_note(db, note_id)
    if note is None or note.is_deleted:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    if note.owner_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    logging.info(f"Пользователь {current_user.username} запросил заметку с ID {note_id}")
    return note


# Обновление заметки
@app.put("/notes/{note_id}", response_model=schemas.NoteResponse)
def update_note(
        note_id: int,
        note_update: schemas.NoteUpdate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    note = crud.get_note(db, note_id)
    if note is None or note.is_deleted:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    updated_note = crud.update_note(db, note, note_update)
    logging.info(f"Пользователь {current_user.username} обновил заметку с ID {note_id}")
    return updated_note


# Мягкое удаление заметки (флаг is_deleted = True)
@app.delete("/notes/{note_id}", response_model=schemas.NoteResponse)
def delete_note(
        note_id: int,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    note = crud.get_note(db, note_id)
    if note is None or note.is_deleted:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    deleted_note = crud.delete_note(db, note)
    logging.info(f"Пользователь {current_user.username} удалил заметку с ID {note_id}")
    return deleted_note


# ------------------- Эндпоинты для пользователей с ролью "Admin" -------------------

# Получение списка всех заметок (для администратора)
@app.get("/admin/notes/", response_model=list[schemas.NoteResponse])
def admin_get_all_notes(
        current_user: models.User = Depends(require_role("Admin")),
        db: Session = Depends(get_db)
):
    notes = crud.get_all_notes(db)
    logging.info(f"Админ {current_user.username} запросил список всех заметок")
    return notes


# Получение заметок конкретного пользователя (для администратора)
@app.get("/admin/notes/user/{user_id}", response_model=list[schemas.NoteResponse])
def admin_get_notes_by_user(
        user_id: int,
        current_user: models.User = Depends(require_role("Admin")),
        db: Session = Depends(get_db)
):
    notes = crud.get_notes_by_user(db, user_id)
    logging.info(f"Админ {current_user.username} запросил заметки пользователя с ID {user_id}")
    return notes


# Восстановление ранее удалённой заметки (для администратора)
@app.post("/admin/notes/{note_id}/restore", response_model=schemas.NoteResponse)
def admin_restore_note(
        note_id: int,
        current_user: models.User = Depends(require_role("Admin")),
        db: Session = Depends(get_db)
):
    note = crud.get_note(db, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    if not note.is_deleted:
        raise HTTPException(status_code=400, detail="Заметка не удалена")
    restored_note = crud.restore_note(db, note)
    logging.info(f"Админ {current_user.username} восстановил заметку с ID {note_id}")
    return restored_note


# Запуск приложения через uvicorn (если запустить файл напрямую)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)