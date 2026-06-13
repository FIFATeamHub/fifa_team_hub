FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage/uploads

EXPOSE 5000

CMD ["sh", "-c", "mkdir -p /app/storage/uploads && chmod -R 777 /app/storage/uploads && python run.py"]