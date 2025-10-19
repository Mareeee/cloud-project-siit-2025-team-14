import os
import boto3
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])

def handler(event, context):
    response = genres_table.scan()
    return create_response(200, {"data": response.get("Items", [])})