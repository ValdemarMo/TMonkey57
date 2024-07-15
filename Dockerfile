# Используем базовый образ Alpine Linux
FROM alpine:latest

# Установим необходимые пакеты
RUN apk add --no-cache python3 py3-pip py3-virtualenv

# Создадим рабочую директорию внутри контейнера
WORKDIR /app

# Скопируем файлы приложения в рабочую директорию
COPY . /app

# Создадим и активируем виртуальную среду
RUN python3 -m venv /app/venv

# Установим зависимости в виртуальную среду
RUN /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

# Укажем команду для запуска приложения
CMD ["/app/venv/bin/python", "main.py"]

