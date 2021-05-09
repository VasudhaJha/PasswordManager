import os
import json
import boto3
from cryptography.fernet import Fernet

dynamodb = boto3.resource('dynamodb')
s3 = boto3.resource('s3')
vault_table = dynamodb.Table(os.environ.get('VAULT_TABLE_NAME'))
vault_table_partition_key = os.environ.get('VAULT_TABLE_KEY')
vault_table_sort_key = os.environ.get('VAULT_SORT_KEY')
bucket_name = os.environ.get('S3_BUCKET_NAME')
key_file_name = os.environ.get('ENCRYPTION_KEY')
key_file_destination = "/tmp/" + key_file_name
s3.meta.client.download_file(Bucket=bucket_name, Key=key_file_name, Filename=key_file_destination)
key = open(key_file_destination, "rb").read()

def _create_vault_item(email, name, item_type, value):
    vault_table.put_item(
        Item={
            vault_table_partition_key: email,
            vault_table_sort_key: name,
            'type': item_type,
            'value': value
        }
    )

def _encrypt_item_value(value):
    encoded_value = value.encode("utf-8")
    f = Fernet(key)
    return f.encrypt(encoded_value)

def lambda_handler(event, context):
    print(f"event: {event}")
    request_body = json.loads(event['body'])
    print(request_body)
    email = request_body['email']
    name = request_body['name']
    item_type = request_body['type']
    value = request_body['value']
    print(email, name, item_type, value)

    value_string = str(value).replace("'", "\"")
    print(f"value_string: {value_string}")
    encrypted_value = _encrypt_item_value(value_string)
    print(f"encrypted_value: {encrypted_value}")
    _create_vault_item(email=email, name=name, item_type=item_type, value=encrypted_value)

    return {
        "statusCode": 201,
        "headers": {
            "Content-Type": "application/json"
        }
    }