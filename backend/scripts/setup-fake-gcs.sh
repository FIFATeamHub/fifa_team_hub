#!/bin/bash

BUCKET_NAME="${GCS_BUCKET_NAME:-fifa-team-hub-documents}"
FAKE_GCS_URL="${FAKE_GCS_URL:-http://fake-gcs:4443}"
PROJECT_ID="${GCP_PROJECT_ID:-fifa-team-hub}"

echo "Aguardando fake-gcs em ${FAKE_GCS_URL}..."
until curl -sf -o /dev/null "${FAKE_GCS_URL}/storage/v1/b?project=${PROJECT_ID}"; do
  sleep 1
done

# Idempotente: só cria o bucket se ele ainda não existir
if curl -sf -o /dev/null "${FAKE_GCS_URL}/storage/v1/b/${BUCKET_NAME}"; then
  echo "✓ Bucket ${BUCKET_NAME} já existe no fake-gcs"
else
  curl -X POST "${FAKE_GCS_URL}/storage/v1/b?project=${PROJECT_ID}" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"${BUCKET_NAME}\"}"

  echo ""
  echo "✓ Bucket ${BUCKET_NAME} criado no fake-gcs"
fi

# Listar buckets
curl -X GET "${FAKE_GCS_URL}/storage/v1/b?project=${PROJECT_ID}"