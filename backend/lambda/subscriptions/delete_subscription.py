import json
import os
import boto3
from utils.utils import create_response

sns = boto3.client("sns")
TOPIC_ARN = os.environ.get("TOPIC_ARN")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    try:
        subscription_id = event.get("queryStringParameters", {}).get("subscriptionId")
        if not subscription_id:
            return create_response(400, {"message": "subscriptionId is required."})

        response = table.query(
            IndexName="subscriptionId-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("subscriptionId").eq(subscription_id)
        )
        items = response.get("Items", [])
        if not items:
            return create_response(404, {"message": "Subscription not found."})

        item = items[0]
        table.delete_item(Key={"userId": item["userId"], "targetId": item["targetId"]})

        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps({
                "eventType": "user_unsubscribed",
                "userId": item["userId"],
                "targetId": item["targetId"],
                "targetType": item["targetType"]
            })
        )

        return create_response(200, {"message": f"Unsubscribed successfully."})

    except Exception as e:
        return create_response(500, {"message": str(e)})
