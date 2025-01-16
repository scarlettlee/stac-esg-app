#!/bin/bash

# Set your GCP project ID
PROJECT_ID="esgreen-mvp"
APP_NAME="stac-esg-app"
REGION="us-central1"

# Build the container
echo "Building container..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${APP_NAME}

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${APP_NAME} \
    --image gcr.io/${PROJECT_ID}/${APP_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --min-instances=0 \
    --max-instances=1 \
    --memory=1Gi

echo "Deployment complete!"