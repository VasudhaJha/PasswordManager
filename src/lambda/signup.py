import os
import json
import boto3

def _add_user(email, first_name, last_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ.get('USER_TABLE_NAME'))
    print(f"Adding user with email: {email}, first name: {first_name}, last name: {last_name}")
    table.put_item(
        Item={
            os.environ.get('USER_TABLE_KEY'): email,
            'first_name': first_name,
            'last_name': last_name,
        }
    )

def lambda_handler(event, context): 
    request_body = json.loads(event['body'])
    
    first_name = request_body['firstName']
    last_name = request_body['lastName']
    email = request_body['email']

    _add_user(email, first_name, last_name)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        }
    }
