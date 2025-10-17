import os
import boto3
from artists.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])

def get_genre_id_by_name(genre_name):
    response = genres_table.scan(
        FilterExpression="#n = :g",
        ExpressionAttributeNames={"#n": "name"},
        ExpressionAttributeValues={":g": genre_name}
    )
    items = response.get("Items", [])
    if items:
        return items[0]["id"]
    return None

def handler(event, context):
    try:
        genre_name = event["pathParameters"].get("genre")
        if not genre_name:
            return create_response(400, {"message": "Genre parameter required."})

        genre_id = get_genre_id_by_name(genre_name)
        if not genre_id:
            return create_response(404, {"message": f"Genre '{genre_name}' not found."})

        response = artists_table.scan(
            FilterExpression="contains(genreIds, :gid)",
            ExpressionAttributeValues={":gid": genre_id}
        )

        artists = response.get("Items", [])

        return create_response(200, {"data": artists})

    except Exception as e:
        return create_response(500, {"message": str(e)})
