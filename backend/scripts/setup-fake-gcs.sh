#!/bin/bash

BUCKET_NAME="fifa-team-hub-documents"
FAKE_GCS_URL="http://fake-gcs:4443"
PROJECT_ID="test-project"

# Criar bucket
curl -X POST "${FAKE_GCS_URL}/storage/v1/b?project=${PROJECT_ID}" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"${BUCKET_NAME}\"}"

echo ""
echo "✓ Bucket ${BUCKET_NAME} criado no fake-gcs"

# Listar buckets
curl -X GET "${FAKE_GCS_URL}/storage/v1/b?project=${PROJECT_ID}"