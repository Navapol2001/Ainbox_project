#!/bin/bash

PROJECT_ID="your-project-id"
REGION="asia-southeast1"

# Create NEGs
gcloud compute network-endpoint-groups create ainbox-neg --region=$REGION --network-endpoint-type=serverless --cloud-run-service=ainbox
gcloud compute network-endpoint-groups create backend-neg --region=$REGION --network-endpoint-type=serverless --cloud-run-service=backend
gcloud compute network-endpoint-groups create protal-neg --region=$REGION --network-endpoint-type=serverless --cloud-run-service=protal
gcloud compute network-endpoint-groups create landingpage-neg --region=$REGION --network-endpoint-type=serverless --cloud-run-service=landingpage

# Create backend services
gcloud compute backend-services create ainbox-backend --global --load-balancing-scheme=EXTERNAL_MANAGED
gcloud compute backend-services create backend-backend --global --load-balancing-scheme=EXTERNAL_MANAGED
gcloud compute backend-services create protal-backend --global --load-balancing-scheme=EXTERNAL_MANAGED
gcloud compute backend-services create landingpage-backend --global --load-balancing-scheme=EXTERNAL_MANAGED

# Add NEGs to backend services
gcloud compute backend-services add-backend ainbox-backend --global --network-endpoint-group=ainbox-neg --network-endpoint-group-region=$REGION
gcloud compute backend-services add-backend backend-backend --global --network-endpoint-group=backend-neg --network-endpoint-group-region=$REGION
gcloud compute backend-services add-backend protal-backend --global --network-endpoint-group=protal-neg --network-endpoint-group-region=$REGION
gcloud compute backend-services add-backend landingpage-backend --global --network-endpoint-group=landingpage-neg --network-endpoint-group-region=$REGION

# Create URL map
gcloud compute url-maps create my-load-balancer --default-service landingpage-backend

# Add path matcher
gcloud compute url-maps add-path-matcher my-load-balancer --path-matcher-name=pathmap --default-service=landingpage-backend --path-rules="/portal/*=protal-backend,/api/*=backend-backend,/ai/*=ainbox-backend"

# Create target HTTP proxy
gcloud compute target-http-proxies create my-load-balancer-proxy --url-map my-load-balancer

# Create forwarding rule
gcloud compute forwarding-rules create http-content-rule --global --target-http-proxy=my-load-balancer-proxy --ports=80 --load-balancing-scheme=EXTERNAL_MANAGED