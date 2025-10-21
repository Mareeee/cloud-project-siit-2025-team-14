import uuid
import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])
sns = boto3.client('sns')
TOPIC_ARN = os.environ['TOPIC_ARN']

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
        title = body.get("title")
        release_date = body.get("releaseDate")
        genres = body.get("genres", [])
        artist_ids = body.get("artistIds", [])

        if not title or not release_date or not genres:
            return create_response(400, {"message": "title, releaseDate and genres are required"})

        album_id = str(uuid.uuid4())
        genre_data = [get_or_create_genre(g) for g in genres]
        genre_ids = [g["id"] for g in genre_data]

        valid_artist_ids = []
        for aid in artist_ids:
            res = artists_table.query(KeyConditionExpression=Key("id").eq(aid))
            if res.get("Items"):
                valid_artist_ids.append(aid)

        item = {
            "id": album_id,
            "title": title,
            "releaseDate": release_date,
            "genreIds": genre_ids,
            "artistIds": valid_artist_ids
        }

        albums_table.put_item(Item=item)

        for g in genre_data:
            genre_catalog_table.put_item(Item={
                "PK": f"GENRE#{g['name']}",
                "SK": f"ALBUM#{album_id}",
                "entityType": "ALBUM",
                "entityId": album_id,
                "title": title,
                "releaseDate": release_date
            })

        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps({
                "targetId": album_id,
                "contentInfo": {
                    "type": "album",
                    "title": title,
                    "releaseDate": release_date,
                }
            })
        )

        return create_response(200, {
            "message": f'Album "{title}" created successfully.',
            "id": album_id,
            "album": item
        })

    except Exception as e:
        return create_response(500, {"message": str(e)})
