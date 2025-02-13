from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal
from .auth import oauth2_scheme, verify_token

# Зависимость для создания сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Зависимость для получения текущего пользователя из JWT токена
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return verify_token(token, db)

# Если потребуется, можно добавить дополнительные проверки (например, активен ли пользователь)
def get_current_active_user(current_user = Depends(get_current_user)):
    return current_user

# Функция-генератор зависимостей для проверки наличия определённой роли у пользователя
def require_role(required_role: str):
    def role_checker(current_user = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав"
            )
        return current_user
    return role_checker