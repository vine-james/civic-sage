import boto3
import botocore
from boto3.dynamodb.conditions import Key
from zoneinfo import ZoneInfo

import utils.constants as constants


def dynamodb_init(table_name):
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=constants.AWS_REGION,
        aws_access_key_id=constants.TOKEN_AWS_ACCESS,
        aws_secret_access_key=constants.TOKEN_AWS_SECRET,
    )

    table = dynamodb.Table(table_name)

    return table


def dynamodb_upload_record(table, data):
    try:
        # NOTE: The partition key value from the table needs to be present in the data dict being passed
        response = table.put_item(Item=data)
        print(f"[{table}]: Item successfully added: {response}")

    except Exception as e:
        print(f"[{table}]: Error uploading data: {e}")


def dynamodb_fetch_record(table, partition_key, partition_key_value):
    try:
        response = table.get_item(Key={partition_key: partition_key_value})

        item = response.get("Item")

        if item:
            return item
        
        else:
            print(f"[{table}]: Item {partition_key_value} not found.")

    except Exception as e:
        print(f"[{table}]: Error fetching item: {e}")


def dynamodb_batch_fetch_records(table, partition_key, partition_key_value):
    try:
        response = table.query(KeyConditionExpression=Key(partition_key).eq(partition_key_value))

        items = response.get("Items", [])


        if items:
            return items
        
        else:
            print(f"[{table}]: Item {partition_key_value} not found.")

    except Exception as e:
        print(f"[{table}]: Error fetching item: {e}")


s3 = boto3.client(
    "s3",
    region_name=constants.AWS_REGION,
    aws_access_key_id=constants.TOKEN_AWS_ACCESS,
    aws_secret_access_key=constants.TOKEN_AWS_SECRET,
)


def s3_upload(local_file_path, cloud_file_path):
    s3.put_object(Body=local_file_path, Bucket="civic-sage", Key=cloud_file_path)


def s3_get_file(file_key):
    try:
        obj = s3.get_object(Bucket="civic-sage", Key=file_key)
        return obj["Body"].read().decode("utf-8")
    
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            print(f"{file_key} does not exist")
        
        print(e.response)
        return None


def s3_batch_get_all_files():

    objects = []
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket="civic-sage"):
        for obj in page.get("Contents", []):
            objects.append(obj["Key"])

    all_files = []
    for key in objects:
        response = s3.get_object(Bucket="civic-sage", Key=key)
        content = response["Body"].read()
        
        all_files.append({"filename": key, "content": content, "modified": response["LastModified"].astimezone(ZoneInfo("Europe/London"))})

    return all_files