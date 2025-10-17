import os
import boto3
from songs.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["ARTISTS_TABLE"])

def handler(event, context):
    try:
        genre = event["pathParameters"].get("genre")
        if not genre:
            return create_response(400, {"message": "Genre parameter required."})

        response = table.scan(
            FilterExpression="contains(genres, :g)",
            ExpressionAttributeValues={":g": genre},
            ExpressionAttributeNames={"#n": "name"}
        )

        artists = response.get("Items", [])
        for artist in artists:
            if isinstance(artist.get("genres"), set):
                artist["genres"] = list(artist["genres"])

        return create_response(200, {"data": artists})
    except Exception as e:
        return create_response(500, {"message": str(e)})
