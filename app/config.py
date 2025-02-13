from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from datetime import timedelta


class Settings(BaseSettings):
    # Секретный ключ для генерации JWT-токенов. Если отсутствует, задаётся значение по умолчанию.
    secret_key: str = Field("default_secret_key", env="SECRET_KEY")

    # Алгоритм, используемый для подписи JWT.
    algorithm: str = "HS256"

    # Время жизни токена в минутах.
    access_token_expire_minutes: int = 30

    @property
    def access_token_expire(self) -> timedelta:
        """
        Возвращает время жизни токена в виде timedelta.
        """
        return timedelta(minutes=self.access_token_expire_minutes)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Инициализация настроек
settings = Settings()

