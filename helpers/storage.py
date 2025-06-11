# Imports the Google Cloud client library
import io
import os
from google.cloud import storage
from google.oauth2 import service_account
import base64
import json

sa_info = json.loads(base64.b64decode(os.getenv("GCS_SERVICE_ACCOUNT")).decode("utf-8"))
credentials = service_account.Credentials.from_service_account_info(sa_info)

# The name for the new bucket
BUCKET_NAME = "rag_doc_storage"


def upload_to_gcs(file_obj, filename):
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(BUCKET_NAME)
    blob_name = f"uploads/{filename}"
    blob = bucket.blob(blob_name)
    blob.upload_from_file(file_obj)
    return blob_name


def download_from_gcs(blob_name: str):
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    content = blob.download_as_bytes()
    file_obj = io.BytesIO(content)
    file_obj.seek(0)
    return file_obj, blob.content_type, blob.name.split("/")[-1]


def delete_file_from_gcs(blob_name: str):
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    if blob.exists():
        blob.delete()
        return True
    else:
        return False
