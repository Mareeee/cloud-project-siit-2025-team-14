import os
import boto3
import uuid
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key
from songs.utils.utils import create_response

s3 = boto3.client("s3")
bucket = os.environ["MEDIA_BUCKET"]
dynamodb = boto3.resource("dynamodb")

songs_table = dynamodb.Table(os.environ["SONGS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])
artist_catalog_table = dynamodb.Table(os.environ["ARTIST_CATALOG_TABLE"])

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
        artist_ids = body.get("artistIds")
        genres = body.get("genres")
        album_id = body.get("albumId")
        cover_filename = body.get("coverFilename")
        audio_filename = body.get("audioFilename")

        if not title or not cover_filename or not audio_filename or not artist_ids or not genres:
            return create_response(400, {"message": "All fields are required."})

        song_id = str(uuid.uuid4())
        genre_data = [get_or_create_genre(g) for g in genres]
        genre_ids = [g["id"] for g in genre_data]

        s3_cover_key = f"{song_id}/cover/{cover_filename}"
        s3_audio_key = f"{song_id}/audio/{audio_filename}"

        cover_presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": s3_cover_key},
            ExpiresIn=300
        )

        audio_presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": s3_audio_key},
            ExpiresIn=300
        )

        creation_date = datetime.utcnow().isoformat()

        item = {
            "id": song_id,
            "title": title,
            "artistIds": artist_ids,
            "genreIds": genre_ids,
            "s3KeyCover": s3_cover_key,
            "s3KeyAudio": s3_audio_key,
            "creationDate": creation_date
        }

        if album_id:
            item["album_id"] = album_id

        songs_table.put_item(Item=item)

        for g in genre_data:
            genre_catalog_table.put_item(Item={
                "PK": f"GENRE#{g['name']}",
                "SK": f"SONG#{song_id}",
                "entityType": "SONG",
                "entityId": song_id,
                "title": title,
                "creationDate": creation_date,
                "s3KeyCover": s3_cover_key,
                "s3KeyAudio": s3_audio_key,
                "genres": [g["name"] for g in genre_data]
            })

        for artist_id in artist_ids:
            artist_catalog_table.put_item(Item={
                "PK": f"ARTIST#{artist_id}",
                "SK": f"SONG#{song_id}",
                "entityType": "SONG",
                "entityId": song_id,
                "title": title,
                "creationDate": creation_date,
                "s3KeyCover": s3_cover_key,
                "s3KeyAudio": s3_audio_key,
                "genres": [g["name"] for g in genre_data]
            })

        return create_response(200, {
            "message": f'Song "{title}" ready for upload.',
            "id": song_id,
            "coverUploadUrl": cover_presigned_url,
            "audioUploadUrl": audio_presigned_url
        })

    except Exception as e:
        return create_response(500, {"message": str(e)})
