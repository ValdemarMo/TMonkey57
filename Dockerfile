# Многоэтапная сборка
FROM python:3.9-slim AS builder

# Установим необходимые пакеты
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Создадим рабочую директорию
WORKDIR /app

# Скопируем только необходимые файлы
COPY requirements.txt /app/
RUN python3 -m venv /app/venv \
    && . /app/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app

# Финальный этап
FROM python:3.9-slim

# Скопируем виртуальную среду из первого этапа
COPY --from=builder /app /app

# Укажем рабочую директорию и команду для запуска приложения
WORKDIR /app
CMD ["/app/venv/bin/python", "main.py"]

