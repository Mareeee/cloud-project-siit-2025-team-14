import uuid
import json
import os
import boto3
from songs.utils.utils import create_response
from boto3.dynamodb.conditions import Attr, Key

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])

def get_or_create_genre(genre_name):
    response = genres_table.scan(
        FilterExpression=Attr("name").eq(genre_name)
    )
    items = response.get("Items", [])
    if items:
        return items[0]["id"]

    genre_id = str(uuid.uuid4())
    genres_table.put_item(Item={
        "id": genre_id,
        "name": genre_name
    })
    return genre_id

def handler(event, context):
    try:
        body = json.loads(event["body"])
        title = body.get("title")
        release_date = body.get("releaseDate")
        genres = body.get("genres", [])
        artist_ids = body.get("artistIds", [])

        if not title or not release_date or not genres:
            return create_response(400, {"message": "title, releaseDate and genres are required"})

        album_id = str(uuid.uuid4())
        genre_ids = [get_or_create_genre(g) for g in genres]

        valid_artist_ids = []
        for aid in artist_ids:
            res = artists_table.query(
                KeyConditionExpression=Key("id").eq(aid)
            )
            items = res.get("Items", [])
            if items:
                valid_artist_ids.append(aid)

        item = {
            "id": album_id,
            "title": title,
            "releaseDate": release_date,
            "genreIds": genre_ids,
            "artistIds": valid_artist_ids
        }

        albums_table.put_item(Item=item)

        return create_response(200, {
            "message": f'Album "{title}" created successfully.',
            "id": album_id,
            "album": item
        })

    except Exception as e:
        return create_response(500, {"message": str(e)})
