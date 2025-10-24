import os
import json
import boto3
from utils.utils import create_response

sns = boto3.client("sns")
TOPIC_ARN = os.environ.get("TOPIC_ARN")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["RATINGS_TABLE"])

ALLOWED_RATINGS = {"love": 3, "like": 2, "dislike": 1}

def handler(event, context):
    try:
        body = json.loads(event["body"])
        user_id = body.get("userId")
        content_id = body.get("contentId")
        rating = body.get("rating")

        if not user_id or not content_id or rating not in ALLOWED_RATINGS.keys():
            return create_response(400, {"message": "Invalid input. Allowed ratings: love, like, dislike."})

        table.put_item(Item={
            "contentId": content_id,
            "userId": user_id,
            "rating": rating
        })

        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps({
                "eventType": "user_rated",
                "userId": user_id,
                "contentId": content_id,
                "rating": ALLOWED_RATINGS[rating]
            })
        )

        return create_response(200, {"message": "Rating saved successfully."})
    except Exception as e:
        return create_response(500, {"message": str(e)})
