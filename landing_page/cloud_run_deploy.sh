#!/bin/sh

PROJECT_ID="x-object-425917-m2"

# Build and deploy
gcloud builds submit --tag asia-southeast1-docker.pkg.dev/$PROJECT_ID/test-repo/ainbox_landing_page .
gcloud run deploy landingpage \
    --image asia-southeast1-docker.pkg.dev/$PROJECT_ID/test-repo/ainbox_landing_page \
    --service-account navapol-service@$PROJECT_ID.iam.gserviceaccount.com \
    --platform managed \
    --region asia-southeast1 \
    --allow-unauthenticated \
    --min-instances=1 \
    --max-instances=10 \
    --port 3000 \
    --memory 2Gi \
    --project $PROJECT_ID

