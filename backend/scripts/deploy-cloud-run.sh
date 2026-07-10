#!/bin/bash

PROJECT_ID="fifa-team-hub"
SERVICE_NAME="fifa-team-hub"
REGION="us-central1"
IMAGE_URL="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"
CLOUDSQL_INSTANCE="fifa-team-hub:us-central1:fifa-db-prod"

if [ -z "$DATABASE_URL" ]; then
  echo "Erro: variável DATABASE_URL não definida. Rode: export DATABASE_URL=..."
  exit 1
fi

docker build -t ${IMAGE_URL} ./backend
docker push ${IMAGE_URL}

gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_URL} \
  --platform managed \
  --region ${REGION} \
  --memory 512Mi \
  --timeout 60 \
  --set-env-vars STORAGE_BACKEND=gcs,GCS_BUCKET_NAME=fifa-team-hub-documents,GCP_PROJECT_ID=${PROJECT_ID},DATABASE_URL=${DATABASE_URL},JWT_EXPIRE_MINUTES=30,FRONTEND_URL=https://fifa-team-hub-frontend-655629807167.us-central1.run.app \
  --set-secrets JWT_SECRET_KEY=JWT_SECRET_KEY:latest,SECRET_KEY=SECRET_KEY:latest \
  --service-account fifa-team-hub-app@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-cloudsql-instances=${CLOUDSQL_INSTANCE} \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 10

gcloud run services describe ${SERVICE_NAME} --region ${REGION}
