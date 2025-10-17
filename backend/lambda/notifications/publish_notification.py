import os
import json
import boto3
from notifications.utils.utils import create_response

sns = boto3.client("sns")
TOPIC_ARN = os.environ["TOPIC_ARN"]

def handler(event, context):
    try:
        body = json.loads(event["body"])
        message = {
            "title": body.get("title"),
            "id": body.get("id"),
            "type": body.get("type", "song"),
        }

        sns.publish(TopicArn=TOPIC_ARN, Message=json.dumps(message))
        return create_response(200, {"message": "Notification published successfully."})
    except Exception as e:
        return create_response(500, {"message": str(e)})
