import os
import boto3

dynamodb = boto3.resource('dynamodb')
vault_table = os.environ.get('VAULT_TABLE_NAME')
vault_table_partition_key = os.environ.get('VAULT_TABLE_KEY')
vault_table_sort_key = os.environ.get('VAULT_TABLE_SORT_KEY')

def create_table():
    
    dynamodb.create_table(
        TableName=vault_table,
        KeySchema=[
            {
                'AttributeName': vault_table_partition_key,
                'KeyType': 'HASH'
            },
            {
                'AttributeName': vault_table_sort_key,
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': vault_table_partition_key,
                'AttributeType': 'S'
            },
            {
                'AttributeName': vault_table_sort_key,
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
    


