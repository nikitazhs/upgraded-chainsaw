# Используем официальный минимальный образ Python 3.9
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Обновляем pip и устанавливаем все зависимости из requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь исходный код проекта в рабочую директорию контейнера
COPY . .

# Открываем порт 8000 для доступа к приложению
EXPOSE 8000

# Команда для запуска приложения через uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]