import os
import boto3
import json
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

s3 = boto3.client("s3")
bucket = os.environ["MEDIA_BUCKET"]
dynamodb = boto3.resource("dynamodb")

songs_table = dynamodb.Table(os.environ["SONGS_TABLE"])

sns = boto3.client('sns')
FEED_TOPIC_ARN = os.environ['FEED_TOPIC_ARN']

def handler(event, context):
    try:
        song_id = str(event["pathParameters"]["songId"]).strip()
        user_id = str(event["pathParameters"]["userId"]).strip()

        q = songs_table.query(
            IndexName="SongIdIndex",
            KeyConditionExpression=Key("id").eq(song_id)
        )
        items = q.get("Items", [])
        if not items:
            return create_response(404, {"message": f"Song with id {song_id} not found."})

        event_message = {
            "eventType": "song_listened",
            "songId": song_id,
            "userId": user_id
        }

        sns.publish(
            TopicArn=FEED_TOPIC_ARN,
            Message=json.dumps(event_message)
        )

        return create_response(200, {
            "message": f'Song listened.',
            "id": song_id,
        })

    except Exception as e:
        return create_response(500, {"message": str(e)})
