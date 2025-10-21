import os
import json
import uuid
import boto3
import datetime
from utils.utils import create_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    try:
        body = json.loads(event["body"])

        user_id = body.get("userId")
        target_id = body.get("targetId")
        target_type = body.get("targetType")
        email = body.get("email")

        if not user_id or not target_id or not target_type or not email:
            return create_response(400, {"message": "Missing required fields."})

        subscription_id = str(uuid.uuid4())
        table.put_item(Item={
            "userId": user_id,
            "targetId": target_id,
            "targetType": target_type,
            "email": email,
            "subscriptionId": subscription_id,
            "createdAt": datetime.datetime.utcnow().isoformat()
        })

        return create_response(200, {"message": "Subscribed successfully.", "subscriptionId": subscription_id})
    except Exception as e:
        return create_response(500, {"message": str(e)})
