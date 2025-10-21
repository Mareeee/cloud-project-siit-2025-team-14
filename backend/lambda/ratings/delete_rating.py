import os
import json
import boto3
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["RATINGS_TABLE"])

def handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        user_id = params.get("userId")
        content_id = params.get("contentId")

        if not user_id or not content_id:
            return create_response(400, {"message": "userId and contentId are required."})

        table.delete_item(
            Key={
                "contentId": content_id,
                "userId": user_id
            }
        )

        return create_response(200, {"message": "Rating deleted successfully."})
    except Exception as e:
        return create_response(500, {"message": str(e)})
