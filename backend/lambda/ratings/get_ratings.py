import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["RATINGS_TABLE"])

RATING_VALUES = {"dislike": 1, "like": 2, "love": 3}

def handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        content_id = params.get("contentId")
        user_id = params.get("userId")

        if not content_id:
            return create_response(400, {"message": "contentId is required."})

        if user_id:
            response = table.get_item(Key={"contentId": content_id, "userId": user_id})
            item = response.get("Item")
            if item:
                return create_response(200, {"userRating": item["rating"]})
            else:
                return create_response(200, {"userRating": None})

        response = table.query(KeyConditionExpression=Key("contentId").eq(content_id))
        items = response.get("Items", [])

        if not items:
            return create_response(200, {"averageRating": None, "count": 0})

        numeric_ratings = [RATING_VALUES[item["rating"]] for item in items if item["rating"] in RATING_VALUES]
        avg = sum(numeric_ratings) / len(numeric_ratings)

        return create_response(200, {
            "averageRating": round(avg, 2),
            "count": len(numeric_ratings),
            "details": {
                "love": sum(1 for i in items if i["rating"] == "love"),
                "like": sum(1 for i in items if i["rating"] == "like"),
                "dislike": sum(1 for i in items if i["rating"] == "dislike")
            }
        })
    except Exception as e:
        return create_response(500, {"message": str(e)})
