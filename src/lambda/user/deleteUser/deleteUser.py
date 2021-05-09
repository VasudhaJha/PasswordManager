import os
import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table(os.environ.get('USER_TABLE_NAME'))
user_table_partition_key = os.environ.get('USER_TABLE_KEY')
cred_table = dynamodb.Table(os.environ.get('CRED_TABLE_NAME'))
cred_table_partition_key = os.environ.get('CRED_TABLE_KEY')


def _delete_from_users(email):
    try:
        response = user_table.delete_item(
            Key={
                user_table_partition_key: email,
            }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
        else:
            raise
    else:
        return response


def _delete_from_credentials(email):
    try:
        response = cred_table.delete_item(
            Key={
                cred_table_partition_key: email,
            }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
        else:
            raise
    else:
        return response   


def _delete_user(email):
    _delete_from_users(email)
    _delete_from_credentials(email)
    

def lambda_handler(event, context): 
    email = event['pathParameters']['email']
    _delete_user(email)

    return {
        "statusCode": 204,
        "headers": {
            "Content-Type": "application/json"
        }
    }