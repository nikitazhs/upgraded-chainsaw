from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL подключения к базе данных. Здесь используется SQLite (файл notes.db в корне проекта).
SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"

# Создаем объект Engine для подключения к базе данных.
# Для SQLite используется параметр connect_args, чтобы отключить проверку потоков.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Создаем SessionLocal - класс для создания сессий подключения к базе данных.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей, от которого будут наследоваться все модели SQLAlchemy.
Base = declarative_base()