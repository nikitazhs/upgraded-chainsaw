# Используем официальный минимальный образ Python 3.9
FROM python:3.9-slim

# Устанавливаем переменную окружения для отсутствия буферизации вывода
ENV PYTHONUNBUFFERED=1

# Указываем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости, если они необходимы (например, gcc для сборки некоторых библиотек)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей и устанавливаем их, используя кэширование слоёв Docker
COPY requirements.txt . 
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем остальной исходный код приложения
COPY . .

# Открываем порт 8000 для приложения
EXPOSE 8000

# Команда для запуска приложения с помощью uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
