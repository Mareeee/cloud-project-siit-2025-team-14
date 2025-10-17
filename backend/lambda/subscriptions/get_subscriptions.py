import os
import boto3
from boto3.dynamodb.conditions import Key
from subscriptions.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])

def handler(event, context):
    try:
        user_id = event["queryStringParameters"].get("userId")
        if not user_id:
            return create_response(400, {"message": "User ID required."})

        response = table.query(KeyConditionExpression=Key("userId").eq(user_id))
        return create_response(200, {"data": response.get("Items", [])})
    except Exception as e:
        return create_response(500, {"message": str(e)})
