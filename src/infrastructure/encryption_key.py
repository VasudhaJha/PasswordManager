import os
import boto3
from cryptography.fernet import Fernet

s3 = boto3.resource('s3')
bucket_name = os.environ.get('S3_BUCKET_NAME')
key_file_name = os.environ.get('ENCRYPTION_KEY')

def _generate_key():
    key = Fernet.generate_key()
    with open(key_file_name, "wb") as key_file:
        key_file.write(key)

def upload_key_file():
    _generate_key()
    s3.Bucket(bucket_name).upload_file(Filename=key_file_name, Key=key_file_name)
    os.remove(key_file_name)

if __name__ == "__main__":
    upload_key_file()



