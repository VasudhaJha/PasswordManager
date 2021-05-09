import os
import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
vault_table = dynamodb.Table(os.environ.get('VAULT_TABLE_NAME'))
vault_table_partition_key = os.environ.get('VAULT_TABLE_KEY')
vault_table_sort_key = os.environ.get('VAULT_SORT_KEY')

def _delete_vault_item(email, name):
    try:
        vault_table.delete_item(
            Key={
                vault_table_partition_key: email,
                vault_table_sort_key: name
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise

def lambda_handler(event, context):
    email = event['pathParameters']['email']
    name = event['pathParameters']['name']
    _delete_vault_item(email=email, name=name)

    return {
        "statusCode": 204,
        "headers": {
            "Content-Type": "application/json"
        }
    }