FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_DEBUG=0

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:$PORT wsgi:app"]

EXPOSE 5000
