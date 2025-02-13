from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

# Создаем объект для хэширования паролей (используем bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Получение пользователя по username
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# Создание нового пользователя
def create_user(db: Session, user: schemas.UserCreate):
    # Хэширование пароля для безопасности
    hashed_password = pwd_context.hash(user.password)
    # Создаем объект пользователя
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()   # Сохраняем изменения в базе данных
    db.refresh(db_user)  # Обновляем объект, чтобы получить, например, сгенерированный id
    return db_user

# Создание новой заметки
def create_note(db: Session, note: schemas.NoteCreate, user_id: int):
    # Распаковываем данные заметки и добавляем идентификатор владельца
    db_note = models.Note(**note.dict(), owner_id=user_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

# Получение заметки по её id
def get_note(db: Session, note_id: int):
    return db.query(models.Note).filter(models.Note.id == note_id).first()

# Получение заметок, принадлежащих конкретному пользователю и не удалённых
def get_notes_by_owner(db: Session, owner_id: int):
    return db.query(models.Note).filter(
        models.Note.owner_id == owner_id,
        models.Note.is_deleted == False
    ).all()

# Получение всех заметок, не удалённых (для администратора)
def get_all_notes(db: Session):
    return db.query(models.Note).filter(models.Note.is_deleted == False).all()

# Обновление заметки
def update_note(db: Session, note: models.Note, note_update: schemas.NoteUpdate):
    # Получаем только те поля, которые были переданы в запросе (исключая unset значения)
    update_data = note_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)  # Обновляем соответствующее поле модели
    db.commit()
    db.refresh(note)
    return note

# Мягкое удаление заметки (устанавливаем флаг is_deleted в True)
def delete_note(db: Session, note: models.Note):
    note.is_deleted = True
    db.commit()
    db.refresh(note)
    return note

# Восстановление ранее удалённой заметки (сброс флага is_deleted)
def restore_note(db: Session, note: models.Note):
    note.is_deleted = False
    db.commit()
    db.refresh(note)
    return note

# Получение всех заметок конкретного пользователя (может возвращать и удалённые, если потребуется)
def get_notes_by_user(db: Session, user_id: int):
    return db.query(models.Note).filter(models.Note.owner_id == user_id).all()