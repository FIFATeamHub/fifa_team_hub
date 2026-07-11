#!/bin/bash
set -e

if [ -z "$DATABASE_URL" ]; then
  echo "Erro: variável DATABASE_URL não definida. Rode: export DATABASE_URL=..."
  exit 1
fi

PROJECT_ID="fifa-team-hub"
REGION="us-central1"
BACKEND_URL="https://fifa-team-hub-655629807167.us-central1.run.app"

BACKEND_SERVICE_NAME="fifa-team-hub"
BACKEND_IMAGE_URL="gcr.io/${PROJECT_ID}/${BACKEND_SERVICE_NAME}:latest"
INSTANCE_CONN_NAME=$(gcloud sql instances describe fifa-db-prod --format="value(connectionName)")

FRONTEND_SERVICE_NAME="fifa-team-hub-frontend"
FRONTEND_IMAGE_URL="gcr.io/${PROJECT_ID}/${FRONTEND_SERVICE_NAME}:latest"

echo "==> Deploy do backend"

docker build -t ${BACKEND_IMAGE_URL} ./backend
docker push ${BACKEND_IMAGE_URL}

gcloud run deploy ${BACKEND_SERVICE_NAME} \
  --image ${BACKEND_IMAGE_URL} \
  --platform managed \
  --region ${REGION} \
  --memory 512Mi \
  --timeout 60 \
  --add-cloudsql-instances "${INSTANCE_CONN_NAME}" \
  --set-env-vars STORAGE_BACKEND=gcs,GCS_BUCKET_NAME=fifa-team-hub-documents,GCP_PROJECT_ID=${PROJECT_ID},CLOUD_SQL_INSTANCE_NAME="${INSTANCE_CONN_NAME}",GOOGLE_CLOUD_PROJECT=${PROJECT_ID} \
  --service-account fifa-team-hub-app@${PROJECT_ID}.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 10

gcloud run services describe ${BACKEND_SERVICE_NAME} --region ${REGION}

echo "==> Deploy do frontend"

docker build --build-arg VITE_API_URL=${BACKEND_URL} -t ${FRONTEND_IMAGE_URL} ./frontend
docker push ${FRONTEND_IMAGE_URL}

gcloud run deploy ${FRONTEND_SERVICE_NAME} \
  --image ${FRONTEND_IMAGE_URL} \
  --platform managed \
  --region ${REGION} \
  --memory 256Mi \
  --port 8080 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 5

gcloud run services describe ${FRONTEND_SERVICE_NAME} --region ${REGION}
