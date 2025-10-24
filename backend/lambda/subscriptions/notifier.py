import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
ses = boto3.client('ses')
SOURCE_EMAIL = os.environ['SOURCE_EMAIL']

def handler(event, context):
    try:
        for record in event['Records']:
            message = json.loads(record['Sns']['Message'])
            target_id = message.get('targetId')
            content_info = message.get('contentInfo')

            if not target_id or not content_info:
                print("Skipping invalid message:", message)
                continue

            response = table.query(
                IndexName="targetId-index",
                KeyConditionExpression=Key("targetId").eq(target_id)
            )

            subscribers = response.get("Items", [])
            for sub in subscribers:
                send_email(sub["email"], target_id, content_info)

        return {"statusCode": 200, "body": json.dumps({"message": "Processed SNS event."})}

    except Exception as e:
        print("Error:", e)
        return {"statusCode": 500, "body": str(e)}


def send_email(to_email, target_id, content_info):
    content_type = content_info.get("type")

    if content_type == "artist":
        subject = f"New Artist Created: {content_info['name']}"
        body = f"Artist Name: {content_info['name']}\nBiography: {content_info['biography']}"
    elif content_type == "album":
        subject = f"New Album Released: {content_info['title']}"
        body = f"Album Title: {content_info['title']}\nRelease Date: {content_info['releaseDate']}"
    elif content_type == "song":
        subject = f"New Song Available: {content_info['title']}"
        body = f"Song Title: {content_info['title']}\nRelease Date: {content_info['releaseDate']}"
    else:
        subject = f"New Content: {target_id}"
        body = json.dumps(content_info, indent=2)

    ses.send_email(
        Source=SOURCE_EMAIL,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}},
        },
    )
