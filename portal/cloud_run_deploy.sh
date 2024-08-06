#!/bin/sh

# Build and deploy
gcloud builds submit --tag asia-southeast1-docker.pkg.dev/x-object-425917-m2/test-repo/ainbox_portal .
gcloud run deploy protal \
    --image asia-southeast1-docker.pkg.dev/x-object-425917-m2/test-repo/ainbox_portal \
    --service-account navapol-service@x-object-425917-m2.iam.gserviceaccount.com \
    --platform managed \
    --region asia-southeast1 \
    --no-allow-unauthenticated \
    --min-instances=1 \
    --max-instances=10 \
    --port 3001 \
    --memory 2Gi