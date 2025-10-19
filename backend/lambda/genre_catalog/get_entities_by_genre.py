import os
import boto3
from boto3.dynamodb.conditions import Key
from songs.utils.utils import create_response

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])
bucket_name = os.environ["MEDIA_BUCKET_NAME"]

def handler(event, context):
    try:
        genre = event["pathParameters"].get("genre")
        if not genre:
            return create_response(400, {"message": "Genre parameter required."})

        response = genre_catalog_table.query(
            KeyConditionExpression=Key("PK").eq(f"GENRE#{genre}")
        )

        items = response.get("Items", [])

        for song in items:
            if song.get("entityType") != "SONG":
                continue

            if song.get("s3KeyAudio"):
                song["audioUrl"] = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket_name, "Key": song["s3KeyAudio"]},
                    ExpiresIn=600
                )
            if song.get("s3KeyCover"):
                song["imageUrl"] = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket_name, "Key": song["s3KeyCover"]},
                    ExpiresIn=600
                )

        return create_response(200, {"data": items})

    except Exception as e:
        return create_response(500, {"message": str(e)})
