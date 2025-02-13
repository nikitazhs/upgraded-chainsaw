from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal
from .auth import oauth2_scheme, verify_token
from .models import User  # Предполагается, что ваша модель пользователя называется User


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для создания сессии базы данных.

    Возвращает:
        Генератор сессий SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    """
    Зависимость для получения текущего пользователя из JWT токена.

    Аргументы:
        token: JWT токен, извлекаемый через OAuth2PasswordBearer.
        db: Сессия базы данных.

    Возвращает:
        Объект пользователя, полученный через verify_token.

    Выбрасывает:
        HTTPException с кодом 401, если токен недействителен или пользователь не найден.
    """
    return verify_token(token, db)


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Зависимость для получения активного пользователя.

    В настоящий момент функция просто возвращает текущего пользователя,
    но может быть расширена дополнительной проверкой (например, проверки статуса аккаунта).

    Возвращает:
        Объект пользователя.
    """
    return current_user


def require_role(required_role: str):
    """
    Фабрика зависимостей для проверки наличия у пользователя определенной роли.

    Аргументы:
        required_role: Роль, которую должен иметь пользователь для доступа к маршруту.

    Возвращает:
        Зависимость, которая проверяет роль пользователя и возвращает его, если проверка пройдена.

    Выбрасывает:
        HTTPException с кодом 403, если у пользователя недостаточно прав.
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав"
            )
        return current_user

    return role_checker
