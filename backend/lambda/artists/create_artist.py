import os
import boto3
import uuid
import json
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])

def get_or_create_genre(genre_name):
    response = genres_table.query(
        IndexName="GenreNameIndex",
        KeyConditionExpression=Key("name").eq(genre_name)
    )
    items = response.get("Items", [])
    if items:
        return {"id": items[0]["id"], "name": items[0]["name"]}

    genre_id = str(uuid.uuid4())
    genres_table.put_item(Item={"id": genre_id, "name": genre_name})
    return {"id": genre_id, "name": genre_name}

def handler(event, context):
    try:
        body = json.loads(event["body"])
        name = body.get("name")
        biography = body.get("biography", "")
        genres = body.get("genres", [])

        if not name or not genres:
            return create_response(400, {"message": "Name and at least one genre are required."})

        genre_data = [get_or_create_genre(g) for g in genres]
        genre_ids = [g["id"] for g in genre_data]

        artist_id = str(uuid.uuid4())
        item = {
            "id": artist_id,
            "name": name,
            "biography": biography,
            "genreIds": genre_ids
        }

        artists_table.put_item(Item=item)

        for g in genre_data:
            genre_catalog_table.put_item(Item={
                "PK": f"GENRE#{g['name']}",
                "SK": f"ARTIST#{artist_id}",
                "entityType": "ARTIST",
                "entityId": artist_id,
                "name": name
            })

        return create_response(200, {
            "message": f"Artist '{name}' created successfully!",
            "artist": item
        })

    except Exception as e:
        return create_response(500, {"message": str(e)})
