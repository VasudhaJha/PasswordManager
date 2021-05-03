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

def _update_credentials(email, password):
    hashed_pw = _generate_hashed_password(password)
    cred_table.update_item(
        Key={
            'email': email
        },
        UpdateExpression="set hashed_password=:p",
        ExpressionAttributeValues={
            ":p": hashed_pw
        }
    )

def _update_users(email, first_name, last_name):
    attributes = []
    values = {}
    if first_name:
        attributes.append("first_name=:f")
        values[":f"] = first_name
    if last_name:
        attributes.append("last_name=:l")
        values[":l"] = last_name
    
    update_expression = "set " + ', '.join(attributes)

    user_table.update_item(
        Key={
            'email': email
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=values
    )

def _update_user(email, **kwargs):
    new_first_name = new_last_name = None
    for key, value in kwargs.items():
        if key == "password" and value:
            _update_credentials(email, password=value)
        else:
            if value:
                if key == "first_name":
                    new_first_name = value
                elif key == "last_name":
                    new_last_name = value
    
    if new_first_name or new_last_name:
        _update_users(email, new_first_name, new_last_name)


def lambda_handler(event, context): 
    print(event)
    email = event['pathParameters']['email']
    request_body = json.loads(event['body'])
    password = request_body.get('password')
    first_name = request_body.get('first_name')
    last_name = request_body.get('last_name')

    _update_user(email, password=password, first_name=first_name, last_name=last_name)

    return {
        "statusCode": 204,
        "headers": {
            "Content-Type": "application/json"
        }
    }