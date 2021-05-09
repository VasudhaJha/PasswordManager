import os
import json
import boto3
from botocore.exceptions import ClientError
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

def _decrypt_item_value(value):
    f = Fernet(key)
    decrypted_value = f.decrypt(value)
    return decrypted_value.decode("utf-8")


def _get_vault_item(email, name):
    try:
        response = vault_table.get_item(
            Key={
                vault_table_partition_key: email,
                vault_table_sort_key: name
            }
        )
    except Exception as e:
        print(e)
        raise
    else:
        return response['Item']


def lambda_handler(event, context):
    email = event['pathParameters']['email']
    name = event['pathParameters']['name']

    try:
        response = _get_vault_item(email, name)
        del response['email']
        print(f"RESPONSE: {response}")
        response['value'] = json.loads(_decrypt_item_value(response['value'].value))
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(response)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": str(e)
        }