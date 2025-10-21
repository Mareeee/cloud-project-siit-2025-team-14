import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
ses = boto3.client('ses')
SOURCE_EMAIL = os.environ['SOURCE_EMAIL']

def handler(event, context):
    try:
        body = json.loads(event['body'])
        content_value = body.get('targetId')
        content_info = body.get('contentInfo')

        if not content_value or not content_info:
            return create_response(400, {"message": "Missing 'targetId' or 'contentInfo'."})

        response = table.query(
            IndexName="targetId-index",
            KeyConditionExpression=Key("targetId").eq(content_value)
        )

        subscribers = response.get("Items", [])
        notified_count = 0

        for sub in subscribers:
            send_email(sub["email"], content_value, content_info)
            notified_count += 1

        return create_response(200, {"message": f"Notified {notified_count} users."})

    except Exception as e:
        return create_response(500, {"message": str(e)})


def send_email(to_email, content_value, content_info):
    ses.send_email(
        Source=SOURCE_EMAIL,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": f"New Content: {content_value}"},
            "Body": {
                "Text": {"Data": f"New content has been uploaded:\n\n{json.dumps(content_info, indent=2)}"}
            },
        },
    )
