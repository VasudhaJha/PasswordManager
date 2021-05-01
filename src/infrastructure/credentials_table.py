import boto3
from constants import *

dynamodb = boto3.resource('dynamodb')

def create_table():
    
    dynamodb.create_table(
        TableName=CREDENTIALS_TABLE_NAME,
        KeySchema=[
            {
                'AttributeName': CREDENTIALS_TABLE_KEY,
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': CREDENTIALS_TABLE_KEY,
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

def delete_table():
    table = dynamodb.Table(CREDENTIALS_TABLE_NAME)
    table.delete_table()

if __name__ == "__main__":
    create_table()
    


