import os
import boto3
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])

def handler(event, context):
    try:
        user_id = event["queryStringParameters"].get("userId")
        target_id = event["pathParameters"].get("targetId")

        if not user_id or not target_id:
            return create_response(400, {"message": "User ID and Target ID required."})

        table.delete_item(Key={"userId": user_id, "targetId": target_id})
        return create_response(200, {"message": "Unsubscribed successfully."})
    except Exception as e:
        return create_response(500, {"message": str(e)})
