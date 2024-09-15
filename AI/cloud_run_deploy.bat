@echo off

REM This command submits a build to Google Cloud Build using the specified tag.
call gcloud builds submit --tag gcr.io/ace-memento-422711-q6/ainbox .

REM This command deploys the specified image to Google Cloud Run.
REM The deployed service will be named "ainbox" and will use the specified image.
REM It will run on the managed platform in the "asia-southeast1" region.
REM The service will allow unauthenticated access.
call gcloud run deploy ainbox --image gcr.io/ace-memento-422711-q6/ainbox --platform managed --region asia-southeast1 --allow-unauthenticated