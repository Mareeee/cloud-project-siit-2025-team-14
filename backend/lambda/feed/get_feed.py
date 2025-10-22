import os
import json
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
feed_table = dynamodb.Table(os.environ["FEED_TABLE"])

def handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        user_id = params.get("userId")
        if not user_id:
            return create_response(400, {"message": "Missing userId."})

        response = feed_table.query(
            KeyConditionExpression=Key("userId").eq(user_id),
            ScanIndexForward=False,
            Limit=20
        )

        items = response.get("Items", [])
        return create_response(200, {"feed": items})
    except Exception as e:
        return create_response(500, {"message": str(e)})
