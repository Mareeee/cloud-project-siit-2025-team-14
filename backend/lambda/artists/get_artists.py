import os
import boto3
from songs.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["ARTISTS_TABLE"])

def handler(event, context):
    try:
        response = table.scan()
        artists = response.get("Items", [])

        for artist in artists:
            genres = artist.get("genres", [])
            if isinstance(genres, set):
                artist["genres"] = list(genres)
            elif not isinstance(genres, list):
                artist["genres"] = [str(genres)]

        return create_response(200, {"data": artists})

    except Exception as e:
        return create_response(500, {"message": str(e)})
