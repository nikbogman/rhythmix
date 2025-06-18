import json
import boto3
from botocore.exceptions import ClientError

s3 = boto3.resource(
    "s3",
    endpoint_url="https://03cb0a2284e46ed7c20782ac3218cf4f.r2.cloudflarestorage.com",
)

bucket_name = "rhythmix"
bucket = s3.Bucket(bucket_name)


def get_object(key):
    obj = bucket.Object(key)

    try:
        obj.load()
        body = obj.get()["Body"].read().decode("utf-8")
        return json.loads(body)

    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            raise FileNotFoundError(
                f"Object '{key}' not found in bucket '{bucket.name}'"
            )
        else:
            raise


def upload_object(key: str, data):
    obj = bucket.Object(key)
    json_data = json.dumps(data)

    obj.put(Body=json_data, ContentType="application/json")
    return
