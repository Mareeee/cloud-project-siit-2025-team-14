import os
import boto3
from boto3.dynamodb.conditions import Attr
from songs.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])

def handler(event, context):
    try:
        params = event.get("pathParameters") or {}
        genre = params.get("genre")

        if not genre:
            return create_response(400, {"message": "Genre parameter required."})

        genre_res = genres_table.scan(FilterExpression=Attr("name").eq(genre))
        genre_items = genre_res.get("Items", [])
        if not genre_items:
            return create_response(200, {"data": []})
        genre_id = genre_items[0]["id"]

        response = albums_table.scan(
            FilterExpression=Attr("genreIds").contains(genre_id)
        )
        albums = response.get("Items", [])

        return create_response(200, {"data": albums})
    except Exception as e:
        return create_response(500, {"message": str(e)})
