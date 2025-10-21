import os
import boto3
from utils.utils import create_response
import urllib.parse

dynamodb = boto3.resource("dynamodb")
songs_table = dynamodb.Table(os.environ["SONGS_TABLE"])
s3 = boto3.client("s3")
bucket_name = os.environ["MEDIA_BUCKET"]

def handler(event, context):
    try:
        path_params = event.get("pathParameters") or {}
        song_id = path_params.get("songId")
        title = urllib.parse.unquote(path_params.get("title"))

        if not song_id or not title:
            return create_response(400, {"message": "Both songId and title are required."})

        response = songs_table.get_item(Key={"id": song_id, "title": title})
        item = response.get("Item")

        if not item:
            return create_response(404, {"message": "Song not found."})

        audio_key = item.get("s3KeyAudio")
        if not audio_key:
            return create_response(400, {"message": "Audio file not found for this song."})

        presigned_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": audio_key},
            ExpiresIn=3600
        )

        return create_response(200, {
            "songId": song_id,
            "title": title,
            "downloadUrl": presigned_url
        })

    except Exception as e:
        print("Error generating presigned URL:", str(e))
        return create_response(500, {"message": str(e)})