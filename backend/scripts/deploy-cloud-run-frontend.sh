#!/bin/bash

PROJECT_ID="fifa-team-hub"
SERVICE_NAME="fifa-team-hub-frontend"
REGION="us-central1"
IMAGE_URL="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"
BACKEND_URL="https://fifa-team-hub-655629807167.us-central1.run.app"

docker build --build-arg VITE_API_URL=${BACKEND_URL} -t ${IMAGE_URL} ./frontend
docker push ${IMAGE_URL}

gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_URL} \
  --platform managed \
  --region ${REGION} \
  --memory 256Mi \
  --port 8080 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 5

gcloud run services describe ${SERVICE_NAME} --region ${REGION}
