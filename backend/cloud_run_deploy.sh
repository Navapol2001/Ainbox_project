#!/bin/sh

# Change to the backend directory
cd backend

# Build and deploy
gcloud builds submit --tag asia-southeast1-docker.pkg.dev/x-object-425917-m2/test-repo/ainbox_backend .
gcloud run deploy backend \
    --image asia-southeast1-docker.pkg.dev/x-object-425917-m2/test-repo/ainbox_backend \
    --service-account navapol-service@x-object-425917-m2.iam.gserviceaccount.com \
    --platform managed \
    --region asia-southeast1 \
    --no-allow-unauthenticated \
    --min-instances=1 \
    --max-instances=10 \
    --port 3002 \
    --memory 2Gi

