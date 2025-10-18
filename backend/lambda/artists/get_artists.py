import os
import boto3
from artists.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])

def get_genre_names(genre_ids):
    if not genre_ids:
        return []
    names = []
    for gid in genre_ids:
        if not isinstance(gid, str):
            continue
        try:
            res = genres_table.get_item(Key={"id": gid})
            item = res.get("Item")
            if item and "name" in item:
                names.append(item["name"])
        except Exception as e:
            print(f"Error fetching genre {gid}: {e}")
    return names

def handler(event, context):
    try:
        response = artists_table.scan()
        artists = response.get("Items", [])

        for artist in artists:
            genre_ids = artist.get("genreIds", [])
            artist["genres"] = get_genre_names(genre_ids)

        return create_response(200, {"data": artists})

    except Exception as e:
        return create_response(500, {"message": str(e)})
