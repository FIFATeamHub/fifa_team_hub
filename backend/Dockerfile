FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage/uploads

EXPOSE 5000

CMD ["sh", "-c", "mkdir -p /app/storage/uploads && chmod -R 777 /app/storage/uploads && python run.py"]