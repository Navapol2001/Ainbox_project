#!/bin/sh

PROJECT_ID="x-object-425917-m2"

# Build and deploy
gcloud builds submit --tag asia-southeast1-docker.pkg.dev/$PROJECT_ID/test-repo/ainbox_backend .
gcloud run deploy backend \
    --image asia-southeast1-docker.pkg.dev/$PROJECT_ID/test-repo/ainbox_backend \
    --service-account navapol-service@$PROJECT_ID.iam.gserviceaccount.com \
    --platform managed \
    --region asia-southeast1 \
    --no-allow-unauthenticated \
    --min-instances=1 \
    --max-instances=10 \
    --port 3002 \
    --memory 2Gi \
    --project $PROJECT_ID

