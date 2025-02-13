import os

# Секретный ключ для генерации JWT-токенов.
# Можно задавать через переменные окружения для повышения безопасности.
SECRET_KEY = os.environ.get("SECRET_KEY", "you_secret_key")

# Алгоритм, используемый для шифрования и подписи JWT.
ALGORITHM = "HS256"

# Время жизни токена (в минутах)
ACCESS_TOKEN_EXPIRE_MINUTES = 30