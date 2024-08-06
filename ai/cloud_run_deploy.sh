#!/bin/sh

# Change to the ai directory
cd ai

# Build and deploy
gcloud builds submit --tag asia-southeast1-docker.pkg.dev/x-object-425917-m2/test-repo/ainbox_ai .
gcloud run deploy ainbox \
    --image asia-southeast1-docker.pkg.dev/x-object-425917-m2/test-repo/ainbox_ai \
    --service-account navapol-service@x-object-425917-m2.iam.gserviceaccount.com \
    --platform managed \
    --region asia-southeast1 \
    --no-allow-unauthenticated \
    --min-instances=1 \
    --max-instances=10 \
    --port 8080 \
    --memory 2Gi