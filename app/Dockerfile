# Этап сборки
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Этап финального образа
FROM python:3.12-slim

WORKDIR /app

# Копируем установленные зависимости из builder-этапа
COPY --from=builder /install /usr/local

# Копируем оставшиеся файлы проекта
COPY .. .

CMD ["python", "app.py"]