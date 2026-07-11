FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage/uploads

# Cloud Run usa PORT=8080 por padrão
ENV PORT=8080
ENV FLASK_DEBUG=0

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f "http://localhost:${PORT}/health" || exit 1

CMD ["sh", "-c", "mkdir -p /app/storage/uploads && chmod -R 777 /app/storage/uploads && exec gunicorn --bind=0.0.0.0:${PORT} --workers=4 --timeout=60 wsgi:app"]