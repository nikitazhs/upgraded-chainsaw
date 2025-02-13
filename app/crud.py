from typing import Optional, List
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
import logging

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)

# Создаем объект для хэширования паролей (используем bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """
    Получает пользователя по его имени.

    :param db: Сессия SQLAlchemy.
    :param username: Имя пользователя.
    :return: Объект пользователя или None, если пользователь не найден.
    """
    return db.query(models.User).filter_by(username=username).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Создает нового пользователя с хэшированием пароля.

    :param db: Сессия SQLAlchemy.
    :param user: Схема создания пользователя.
    :return: Созданный объект модели User.
    """
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        logger.error("Ошибка при создании пользователя: %s", e)
        raise e
    return db_user

def create_note(db: Session, note: schemas.NoteCreate, user_id: int) -> models.Note:
    """
    Создает новую заметку для пользователя.

    :param db: Сессия SQLAlchemy.
    :param note: Схема создания заметки.
    :param user_id: Идентификатор владельца заметки.
    :return: Созданный объект модели Note.
    """
    db_note = models.Note(**note.dict(), owner_id=user_id)
    try:
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
    except Exception as e:
        db.rollback()
        logger.error("Ошибка при создании заметки: %s", e)
        raise e
    return db_note

def get_note(db: Session, note_id: int) -> Optional[models.Note]:
    """
    Получает заметку по её ID.

    :param db: Сессия SQLAlchemy.
    :param note_id: ID заметки.
    :return: Объект заметки или None, если заметка не найдена.
    """
    return db.query(models.Note).filter_by(id=note_id).first()

def get_notes_by_owner(db: Session, owner_id: int) -> List[models.Note]:
    """
    Получает список заметок, принадлежащих конкретному пользователю (только не удаленные).

    :param db: Сессия SQLAlchemy.
    :param owner_id: Идентификатор владельца.
    :return: Список заметок.
    """
    return db.query(models.Note).filter(
        models.Note.owner_id == owner_id,
        models.Note.is_deleted == False
    ).all()

def get_all_notes(db: Session) -> List[models.Note]:
    """
    Получает список всех заметок, не удалённых (для администратора).

    :param db: Сессия SQLAlchemy.
    :return: Список заметок.
    """
    return db.query(models.Note).filter(models.Note.is_deleted == False).all()

def update_note(db: Session, note: models.Note, note_update: schemas.NoteUpdate) -> models.Note:
    """
    Обновляет заметку с новыми данными из note_update.

    :param db: Сессия SQLAlchemy.
    :param note: Объект заметки, который необходимо обновить.
    :param note_update: Схема обновления заметки.
    :return: Обновленный объект заметки.
    """
    update_data = note_update.dict(exclude_unset=True)
    if not update_data:
        logger.info("Нет данных для обновления заметки с id %s", note.id)
        return note

    for key, value in update_data.items():
        setattr(note, key, value)
    try:
        db.commit()
        db.refresh(note)
    except Exception as e:
        db.rollback()
        logger.error("Ошибка при обновлении заметки с id %s: %s", note.id, e)
        raise e
    return note

def delete_note(db: Session, note: models.Note) -> models.Note:
    """
    Мягко удаляет заметку, устанавливая флаг is_deleted в True.

    :param db: Сессия SQLAlchemy.
    :param note: Объект заметки для удаления.
    :return: Обновленный объект заметки с is_deleted=True.
    """
    note.is_deleted = True
    try:
        db.commit()
        db.refresh(note)
    except Exception as e:
        db.rollback()
        logger.error("Ошибка при удалении заметки с id %s: %s", note.id, e)
        raise e
    return note

def restore_note(db: Session, note: models.Note) -> models.Note:
    """
    Восстанавливает ранее удаленную заметку (сбрасывая флаг is_deleted).

    :param db: Сессия SQLAlchemy.
    :param note: Объект заметки для восстановления.
    :return: Обновленный объект заметки с is_deleted=False.
    """
    note.is_deleted = False
    try:
        db.commit()
        db.refresh(note)
    except Exception as e:
        db.rollback()
        logger.error("Ошибка при восстановлении заметки с id %s: %s", note.id, e)
        raise e
    return note

def get_notes_by_user(db: Session, user_id: int) -> List[models.Note]:
    """
    Получает все заметки конкретного пользователя, включая удаленные.

    :param db: Сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Список заметок пользователя.
    """
    return db.query(models.Note).filter(models.Note.owner_id == user_id).all()
