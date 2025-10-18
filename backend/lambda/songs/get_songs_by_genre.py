import os
import boto3
from songs.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["SONGS_TABLE"])
s3 = boto3.client("s3")
bucket_name = os.environ["MEDIA_BUCKET"]

def handler(event, context):
    try:
        genre = event["pathParameters"].get("genre")
        if not genre:
            return create_response(400, {"message": "Genre parameter required."})

        response = table.scan(
            FilterExpression="contains(genres, :g)",
            ExpressionAttributeValues={":g": genre}
        )

        songs = response.get("Items", [])
        for song in songs:
            genres = song.get("genres", [])
            if isinstance(genres, set):
                song["genres"] = list(genres)
            elif not isinstance(genres, list):
                song["genres"] = [str(genres)]

            audio_key = song.get("s3KeyAudio")
            if audio_key:
                song["audioUrl"] = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket_name, "Key": audio_key},
                    ExpiresIn=600
                )

            cover_key = song.get("s3KeyCover")
            if cover_key:
                song["imageUrl"] = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket_name, "Key": cover_key},
                    ExpiresIn=600
                )

        return create_response(200, {"data": songs})

    except Exception as e:
        return create_response(500, {"message": str(e)})
