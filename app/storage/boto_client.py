import json
from google.cloud import storage
from google.api_core.exceptions import NotFound

client = storage.Client()
bucket_name = "rhythmix"
bucket = client.bucket(bucket_name)


def get_blob(name: str):
    blob = bucket.blob(blob_name=name)
    try:
        content = blob.download_as_text()
        return json.loads(content)
    except NotFound:
        raise FileNotFoundError(f"Object '{name}' not found in bucket '{bucket_name}'")


def upload_blob(name: str, data):
    blob = bucket.blob(blob_name=name)
    blob.upload_from_string(data=json.dumps(data), content_type="application/json")
