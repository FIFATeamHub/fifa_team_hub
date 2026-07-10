#!/bin/bash

PROJECT_ID="fifa-team-hub"
SERVICE_NAME="fifa-team-hub"
REGION="us-central1"
IMAGE_URL="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

docker build -t ${IMAGE_URL} ./backend
docker push ${IMAGE_URL}

gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_URL} \
  --platform managed \
  --region ${REGION} \
  --memory 512Mi \
  --timeout 60 \
  --set-env-vars STORAGE_BACKEND=gcs,GCS_BUCKET_NAME=fifa-team-hub-documents,GCP_PROJECT_ID=${PROJECT_ID} \
  --service-account fifa-team-hub-app@${PROJECT_ID}.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 10

gcloud run services describe ${SERVICE_NAME} --region ${REGION}