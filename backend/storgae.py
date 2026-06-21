import boto3
import os
from dotenv import load_dotenv

load_dotenv()

B2_KEY_ID = os.getenv("B2_KEY_ID")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
B2_BUCKET = os.getenv("B2_BUCKET")
B2_ENDPOINT = os.getenv("B2_ENDPOINT")

s3 = boto3.client(
    "s3",
    endpoint_url=B2_ENDPOINT,
    aws_access_key_id=B2_KEY_ID,
    aws_secret_access_key=B2_APPLICATION_KEY
)

def upload_file(file_path):
    key = os.path.basename(file_path)
    s3.upload_file(file_path, B2_BUCKET, key)
    print(f"Uploaded: {key}")
    return key

def download_file(key, save_path):
    s3.download_file(B2_BUCKET, key, save_path)
    print(f"Downloaded: {key}")

def delete_file(key):
    s3.delete_object(Bucket=B2_BUCKET, Key=key)
    print(f"Deleted from cloud: {key}")