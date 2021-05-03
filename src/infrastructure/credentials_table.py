import os
import boto3

dynamodb = boto3.resource('dynamodb')
cred_table = os.environ.get('CRED_TABLE_NAME')
cred_table_partition_key = os.environ.get('CRED_TABLE_KEY')

def create_table():
    
    dynamodb.create_table(
        TableName=cred_table,
        KeySchema=[
            {
                'AttributeName': cred_table_partition_key,
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': cred_table_partition_key,
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

if __name__ == "__main__":
    create_table()
    


