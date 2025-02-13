from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import crud, models
from .database import SessionLocal
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Определяем схему для авторизации с помощью OAuth2 (используем JWT)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Функция для создания JWT токена
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    # Устанавливаем время истечения токена
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Кодируем данные в JWT токен, используя секретный ключ и алгоритм
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для проверки валидности токена и получения пользователя
def verify_token(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Получаем пользователя по username
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user