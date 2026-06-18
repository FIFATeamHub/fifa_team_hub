FROM python:3.11-slim
 
WORKDIR /app
 
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copiar código
COPY backend/ .
 
# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')"
 
# Cloud Run usa PORT=8080 por padrão
ENV PORT=8080
 
# Rodar com gunicorn (não Flask dev)
CMD exec gunicorn --bind=0.0.0.0:${PORT} --workers=4 --timeout=60 "app:create_app()"