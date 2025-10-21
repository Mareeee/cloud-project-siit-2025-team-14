import os
import boto3
import json
from boto3.dynamodb.conditions import Attr
from utils.utils import create_response

s3 = boto3.client("s3")
bucket = os.environ["MEDIA_BUCKET"]
dynamodb = boto3.resource("dynamodb")
songs_table = dynamodb.Table(os.environ["SONGS_TABLE"])

def handler(event, context):
    song_id = str(event["pathParameters"]["songId"]).strip()

    try:
        response = songs_table.query(
            IndexName="SongIdIndex",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("id").eq(song_id)
        )
        items = response.get("Items", [])
        majketi = items[0]
        if not items:
            return create_response(404, {"message": "Song not found."})
    except Exception as e:
        return create_response(400, {"message": "DynamoDB get_item failed", "error": str(e)})

    if not majketi:
        return create_response(404, {"message": f"Song with id {song_id} not found."})

    return create_response(200, {"message": items})
