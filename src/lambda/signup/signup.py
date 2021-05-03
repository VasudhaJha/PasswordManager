import os
import json
import boto3
import bcrypt

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table(os.environ.get('USER_TABLE_NAME'))
user_table_partition_key = os.environ.get('USER_TABLE_KEY')
cred_table = dynamodb.Table(os.environ.get('CRED_TABLE_NAME'))
cred_table_partition_key = os.environ.get('CRED_TABLE_KEY')

def _generate_hashed_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def _add_credential(email, password):
    hashed = _generate_hashed_password(password)
    cred_table.put_item(
        Item={
            cred_table_partition_key : email,
            'hashed_password': hashed
        }
    )

def _add_user(email, first_name, last_name):
    print(f"Adding user with email: {email}, first name: {first_name}, last name: {last_name}")
    user_table.put_item(
        Item={
            user_table_partition_key : email,
            'first_name': first_name,
            'last_name': last_name,
        }
    )

def lambda_handler(event, context): 
    request_body = json.loads(event['body'])
    first_name = request_body['first_name']
    last_name = request_body['last_name']
    email = request_body['email']
    password = request_body['password']

    _add_user(email, first_name, last_name)
    _add_credential(email, password)

    return {
        "statusCode": 201,
        "headers": {
            "Content-Type": "application/json"
        }
    }
