import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
songs_table = dynamodb.Table(os.environ["SONGS_TABLE"])
s3 = boto3.client("s3")
bucket_name = os.environ["MEDIA_BUCKET"]

def handler(event, context):
    try:
        album_id = event["pathParameters"].get("albumId")
        if not album_id:
            return create_response(400, {"message": "Album ID required."})

        response = songs_table.query(
            IndexName="AlbumIndex",
            KeyConditionExpression=Key("albumId").eq(album_id)
        )

        songs = response.get("Items", [])
        for song in songs:
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

        return create_response(200, {"data": songs})

    except Exception as e:
        return create_response(500, {"message": str(e)})
