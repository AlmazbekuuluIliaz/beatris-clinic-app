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

EXPOSE 8000

# Перед стартом применяем миграции, затем поднимаем uvicorn на всех интерфейсах.
# host=0.0.0.0 обязателен внутри контейнера, иначе порт не пробросится наружу.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
