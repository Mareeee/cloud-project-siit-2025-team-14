import os
import boto3
from songs.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["ALBUMS_TABLE"])

def handler(event, context):
    try:
        genre = event["pathParameters"].get("genre")
        if not genre:
            return create_response(400, {"message": "Genre parameter required."})

        response = table.scan(
            FilterExpression="contains(genres, :g)",
            ExpressionAttributeValues={":g": genre},
            ExpressionAttributeNames={"#t": "title"}
        )

        albums = response.get("Items", [])
        for album in albums:
            if isinstance(album.get("genres"), set):
                album["genres"] = list(album["genres"])

        return create_response(200, {"data": albums})
    except Exception as e:
        return create_response(500, {"message": str(e)})
