import os
import json
import uuid
import boto3
from ratings.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["RATINGS_TABLE"])

def handler(event, context):
    try:
        body = json.loads(event["body"])
        user_id = body.get("userId")
        content_id = body.get("contentId")
        rating = body.get("rating")

        if not user_id or not content_id or rating is None:
            return create_response(400, {"message": "All fields are required."})

        table.put_item(Item={
            "contentId": content_id,
            "userId": user_id,
            "rating": float(rating)
        })

        return create_response(200, {"message": "Rating saved successfully."})
    except Exception as e:
        return create_response(500, {"message": str(e)})
