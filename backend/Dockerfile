FROM python:3.12-slim

# Не писать .pyc, не буферизовать stdout/stderr (логи сразу видны в docker logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Сначала зависимости — слой кэшируется, пока requirements.txt не изменится
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Затем код приложения
COPY . .

# Railway mounts persistent storage at /app/uploads. Keep the initial media
# outside that mount, then copy only missing files when the container starts.
RUN mv /app/uploads /opt/default_uploads && mkdir -p /app/uploads

EXPOSE 8000

# Перед стартом применяем миграции, затем поднимаем uvicorn на всех интерфейсах.
# host=0.0.0.0 обязателен внутри контейнера, иначе порт не пробросится наружу.
CMD ["sh", "-c", "cp -an /opt/default_uploads/. /app/uploads/ && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
