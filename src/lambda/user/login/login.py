import os
import json
import boto3
import bcrypt
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
cred_table = dynamodb.Table(os.environ.get('CRED_TABLE_NAME'))
cred_table_partition_key = os.environ.get('CRED_TABLE_KEY')

def _get_hashed_pw(email):
    try:
        response = cred_table.get_item(Key={cred_table_partition_key: email})
    except ClientError as e:
        raise Exception(e.response['Error']['Message'])
    else:
        if response.get('Item') is None:
            raise Exception(f'User with email {email} not found')
        return response['Item']['hashed_password']

def _verify_credentials(user_pw, hashed_pw):
    return bcrypt.checkpw(user_pw.encode('utf-8'), hashed_pw.encode('utf-8'))

def lambda_handler(event, context): 
    request_body = json.loads(event['body'])
    email = request_body['email']
    password = request_body['password']

    try:
        hashed_pw = _get_hashed_pw(email)
        if _verify_credentials(password, hashed_pw):
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                }
            }

        else:
            return {
                "statusCode": 401,
                "headers": {
                    "Content-Type": "application/json"
                }
            }
    except Exception as e:
        return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": str(e)
            }
