import os
import boto3
from songs.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
songs_table = dynamodb.Table(os.environ["SONGS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
s3 = boto3.client("s3")
bucket_name = os.environ["MEDIA_BUCKET"]

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
        response = songs_table.scan()
        songs = response.get("Items", [])

        for song in songs:
            genre_ids = song.get("genreIds", [])
            song["genres"] = get_genre_names(genre_ids)

            audio_key = song.get("s3KeyAudio")
            if audio_key:
                song["audioUrl"] = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket_name, "Key": audio_key}
                )

            cover_key = song.get("s3KeyCover")
            if cover_key:
                song["imageUrl"] = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket_name, "Key": cover_key}
                )

        return create_response(200, {"data": songs})

    except Exception as e:
        return create_response(500, {"message": str(e)})
