# Используем базовый образ Python
FROM python:3.9

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Обновляем и устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы с зависимостями
COPY requirements.txt /app/

# Устанавливаем зависимости Python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Копируем проект в рабочую директорию
COPY . /app/

# Запускаем приложение
CMD ["python", "main.py"]
