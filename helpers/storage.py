# Imports the Google Cloud client library
import io
import uuid
from google.cloud import storage


# The name for the new bucket
BUCKET_NAME = "rag_doc_storage"


def upload_to_gcs(file_obj, filename):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob_name = f"uploads/{uuid.uuid4()}_{filename}"
    blob = bucket.blob(blob_name)
    blob.upload_from_file(file_obj)
    return blob_name


def download_from_gcs(blob_name: str):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    content = blob.download_as_bytes()
    file_obj = io.BytesIO(content)
    file_obj.seek(0)
    return file_obj, blob.content_type, blob.name.split("/")[-1]


def delete_file_from_gcs(blob_name: str):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    if blob.exists():
        blob.delete()
        return True
    else:
        return False
