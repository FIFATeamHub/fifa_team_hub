BUCKET_NAME="fifa-team-hub-documents"
FAKE_GCS_URL="http://localhost:4443"
 
curl -X PUT "${FAKE_GCS_URL}/${BUCKET_NAME}"
 
echo "✓ Bucket ${BUCKET_NAME} criado no fake-gcs"
 
curl -X GET "${FAKE_GCS_URL}/"