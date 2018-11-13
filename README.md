# Google Cloud File Encrypter Serverless

This sample demonstrates how to upload and download encrypted files in Google Storage using Cloud Functions.


## Functions Code

Upload
See file [functions/gcf-upload-file/main.py](functions/gcf-upload-file/main.py) for the code.
The dependencies are listed in [functions/gcf-upload-file/requirements.txt](functions/gcf-upload-file/requirements.txt).

Download
See file [functions/gcf-download-file/main.py](functions/gcf-download-file/main.py) for the code.
The dependencies are listed in [functions/gcf-download-file/requirements.txt](functions/gcf-download-file/requirements.txt).


## Trigger rules

The functions triggers on http request.


## Storage and Database Structure

Users upload an image to Storage to the auto generated path `/<external ref uuid>/<encrypted uuid>/<filename>` and save the path and file reference in Cloud Datastore.

## Setting up the sample

This sample comes with a Function and web-based UI for testing the function. To configure it:

 1. Create a Google Cloud Project using the [Console](https://console.cloud.google.com).
 1. Create billing account
 1. Enable the Cloud Functions API
 1. Enable the Cloud Datastore API
 1. Enable the Cloud Storage API


## Deploy and test

To test the sample:
 1. Download and install gcloud command line tool (https://cloud.google.com/sdk/install)
 2. From function path [functions/gcf-upload-file/](functions/gcf-upload-file/) execute:
 ```
 export FUNCTION_NAME="gcf-upload-file";
 export BUCKET_NAME="poc-files";
 export KIND_NAME="poc-files";
 gcloud beta functions deploy ${FUNCTION_NAME} --entry-point execute --set-env-vars BUCKET_NAME=${BUCKET_NAME},DS_KIND=${KIND_NAME} --memory 128MB --runtime python37 --trigger-http;
 ```
 3. Return something like that:
```
Deploying function (may take a while - up to 2 minutes)...done.                                                                                                                                            
availableMemoryMb: 128
entryPoint: execute
environmentVariables:
  BUCKET_NAME: poc-files
  DS_KIND: poc-files
httpsTrigger:
  url: https://[zone]-[project id].cloudfunctions.net/gcf-upload-file
labels:
  deployment-tool: cli-gcloud
name: projects/[project id]/locations/[zone]/functions/gcf-upload-file
runtime: python37
serviceAccountEmail: [service account email]
status: ACTIVE
timeout: 60s
updateTime: '2018-11-12T16:05:07Z'
versionId: '1'
```
4. From function path [functions/gcf-download-file/](functions/gcf-download-file/) execute:
 ```
 export FUNCTION_NAME="gcf-download-file";
 export BUCKET_NAME="poc-files";
 export KIND_NAME="poc-files";
 gcloud beta functions deploy ${FUNCTION_NAME} --entry-point execute --set-env-vars BUCKET_NAME=${BUCKET_NAME},DS_KIND=${KIND_NAME} --memory 128MB --runtime python37 --trigger-http;
 ```
 5. Return something like that:
```
Deploying function (may take a while - up to 2 minutes)...done.                                                                                                                                            
availableMemoryMb: 128
entryPoint: execute
environmentVariables:
  BUCKET_NAME: poc-files
  DS_KIND: poc-files
httpsTrigger:
  url: https://[zone]-[project id].cloudfunctions.net/gcf-download-file
labels:
  deployment-tool: cli-gcloud
name: projects/[project id]/locations/[zone]/functions/gcf-download-file
runtime: python37
serviceAccountEmail: [service account email]
status: ACTIVE
timeout: 60s
updateTime: '2018-11-12T16:05:07Z'
versionId: '1'
```
