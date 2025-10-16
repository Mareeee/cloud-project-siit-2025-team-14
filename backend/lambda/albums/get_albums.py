import os
import boto3
from songs.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])

def get_genre_names(genre_ids):
    if not genre_ids:
        return []
    names = []
    for gid in genre_ids:
        res = genres_table.get_item(Key={"id": gid})
        if "Item" in res:
            names.append(res["Item"]["name"])
    return names

def handler(event, context):
    try:
        response = albums_table.scan()
        albums = response.get("Items", [])

        for album in albums:
            genre_ids = album.get("genreIds", [])
            album["genres"] = get_genre_names(genre_ids)

        return create_response(200, {"data": albums})

    except Exception as e:
        return create_response(500, {"message": str(e)})
