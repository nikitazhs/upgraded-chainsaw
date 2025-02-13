from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import crud, models
from .database import SessionLocal
from .config import settings  # Используем наш объект настроек

import logging

logger = logging.getLogger(__name__)

# Определяем схему для авторизации с помощью OAuth2 (используем JWT)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создает JWT-токен с заданными данными и временем истечения.

    :param data: Словарь с данными для кодирования в токене (например, {"sub": username}).
    :param expires_delta: Дополнительное время жизни токена. Если не указано, берется значение из настроек.
    :return: Закодированный JWT-токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or settings.access_token_expire)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    except Exception as e:
        logger.error("Ошибка при кодировании JWT: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при генерации токена"
        )
    return encoded_jwt


def get_db():
    """
    Зависимость для получения сессии базы данных.

    Используйте ее через Depends() в маршрутах FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_token(token: str, db: Session) -> models.User:
    """
    Проверяет валидность JWT-токена и возвращает соответствующего пользователя.

    :param token: JWT-токен.
    :param db: Сессия базы данных.
    :return: Объект пользователя, если токен валиден.
    :raises HTTPException: Если токен недействителен или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: Optional[str] = payload.get("sub")
        if username is None:
            logger.warning("JWT не содержит поле 'sub'")
            raise credentials_exception
    except JWTError as e:
        logger.warning("Ошибка при декодировании JWT: %s", e)
        raise credentials_exception

    user = crud.get_user_by_username(db, username=username)
    if user is None:
        logger.warning("Пользователь с username '%s' не найден", username)
        raise credentials_exception
    return user
