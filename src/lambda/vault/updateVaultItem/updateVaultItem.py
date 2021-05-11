import copy
import os
import json
import boto3
from botocore.exceptions import ClientError, DataNotFoundError
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

def _format_value(value):
    return str(value).replace("'", "\"")


def _encrypt_item_value(value):
    encoded_value = value.encode("utf-8")
    f = Fernet(key)
    return f.encrypt(encoded_value)


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

        if not response or not response['Item']:
            raise DataNotFoundError("Did not find item")
    except Exception as e:
        print(e)
        raise
    else:
        return response['Item']


def _create_vault_item(email, name, item_type, value):
    vault_table.put_item(
        Item={
            vault_table_partition_key: email,
            vault_table_sort_key: name,
            'type': item_type,
            'value': value
        }
    )


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


def _update_vault_item(new_vault_item):
    vault_table.update_item(
        Key={
            vault_table_partition_key: new_vault_item["email"],
            vault_table_sort_key: new_vault_item["name"]
        },
        UpdateExpression="set value=:v",
        ExpressionAttributeValues={
            ':v': new_vault_item["value"]
        }
    )


def _compare_vault_item(existing_vault_item, new_vault_item):
    delete_old_record = False
    new_item = copy.deepcopy(existing_vault_item)
    new_name = new_vault_item.get("name")
    new_vault_item_value = new_vault_item.get("value")
    new_username = new_password = new_url = new_notes = None

    if new_vault_item_value:
        new_username = new_vault_item_value.get("username")
        new_password = new_vault_item_value.get("password")
        new_url = new_vault_item_value.get("url")
        new_notes = new_vault_item_value.get("notes")

    if new_username and new_username != existing_vault_item["value"]["username"]:
        new_item["value"]["username"] = new_username
    
    if new_password and new_password != existing_vault_item["value"]["password"]:
        new_item["value"]["password"] = new_password
    
    if new_url and new_url != existing_vault_item["value"]["url"]:
        new_item["value"]["url"] = new_url
    
    if new_notes and new_notes != existing_vault_item["value"]["notes"]:
        new_item["value"]["notes"] = new_notes

    if new_name and new_name != existing_vault_item["name"]:
        delete_old_record = True
        new_item["name"] = new_name

    new_item["value"] = _encrypt_item_value(_format_value(new_item["value"]))

    if delete_old_record:
        print(f"adding record to dynamodb with email {new_item['email']} and name {new_item['name']}")
        _create_vault_item(email=new_item["email"], name=new_item["name"], item_type=new_item["type"], value=new_item["value"])
        print(f"deleting record from dynamodb with email {existing_vault_item['email']} and name {existing_vault_item['name']}")
        _delete_vault_item(email=existing_vault_item["email"], name=existing_vault_item["name"])
    else:
        print("updating record in dynamodb")
        _update_vault_item(new_item)

    new_item['value'] = json.loads(_decrypt_item_value(new_item['value']))
    return new_item


def lambda_handler(event, context):
    email = event['pathParameters']['email']
    name = event['pathParameters']['name']
    new_vault_item = json.loads(event['body'])

    try:
        existing_vault_item = _get_vault_item(email, name)
        existing_vault_item['value'] = json.loads(_decrypt_item_value(existing_vault_item['value'].value))
        print(f"existing_vault_item: {existing_vault_item}")
        print(f"new_vault_item: {new_vault_item}")
        new_item = _compare_vault_item(existing_vault_item, new_vault_item)
        del new_item["email"]
        print(f"new_item: {new_item}")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(new_item)
        }
    except DataNotFoundError as d:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": str(d)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": str(e)
        }
