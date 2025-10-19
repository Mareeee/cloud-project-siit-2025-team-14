import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["RATINGS_TABLE"])

def handler(event, context):
    try:
        content_id = event["queryStringParameters"].get("contentId")
        if not content_id:
            return create_response(400, {"message": "contentId is required."})

        response = table.query(KeyConditionExpression=Key("contentId").eq(content_id))
        items = response.get("Items", [])

        if not items:
            return create_response(200, {"averageRating": None, "count": 0})

        avg = sum(float(item["rating"]) for item in items) / len(items)
        return create_response(200, {"averageRating": round(avg, 2), "count": len(items)})
    except Exception as e:
        return create_response(500, {"message": str(e)})
