import uuid
import json
import os
import boto3
from songs.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["ARTISTS_TABLE"])

def handler(event, context):
    try:
        body = json.loads(event["body"])
        name = body.get("name")
        biography = body.get("biography")
        genres = body.get("genres")

        if not name or not biography or not genres:
            return create_response(400, {"message": "name, biography and genres required"})

        artist_id = str(uuid.uuid4())

        table.put_item(Item={
            "id": artist_id,
            "name": name,
            "biography": biography,
            "genres": genres
        })

        return create_response(200, {
            "message": f'Artist "{name}" created',
            "id": artist_id
        })

    except Exception as e:
        return create_response(500, {"message": str(e)})
