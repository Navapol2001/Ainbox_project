#!/bin/sh

# Build and deploy
gcloud builds submit --tag asia-southeast1-docker.pkg.dev/x-object-425917-m2/test-repo/ainbox_landing_page .
gcloud run deploy landingpage \
    --image asia-southeast1-docker.pkg.dev/x-object-425917-m2/test-repo/ainbox_landing_page \
    --service-account navapol-service@x-object-425917-m2.iam.gserviceaccount.com \
    --platform managed \
    --region asia-southeast1 \
    --no-allow-unauthenticated \
    --min-instances=1 \
    --max-instances=10 \
    --port 3000 \
    --memory 2Gi

