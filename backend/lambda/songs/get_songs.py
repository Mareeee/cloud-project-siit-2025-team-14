import os
import boto3
from songs.utils.utils import create_response
from datetime import datetime

table_name = os.environ['SONGS_TABLE']
bucket_name = os.environ['MEDIA_BUCKET']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
s3 = boto3.client('s3')


def handler(event, context):
    try:
        response = table.scan()
        items = response.get('Items', [])

        songs_data = []

        for item in items:
            song = {
                "id": item.get("id"),
                "title": item.get("title"),
                "artistId": item.get("artistId", None),
                "albumId": item.get("albumId", None),
                "creationDate": item.get("creationDate", None),
                "genres": list(item.get("genres", []))
            }

            media = item.get("media", {})
            for media_type in ["audio", "image"]:
                s3_key = media.get(media_type)
                if s3_key:
                    try:
                        s3_head = s3.head_object(Bucket=bucket_name, Key=s3_key)
                        song[f"{media_type}FileName"] = s3_key.split('/')[-1]
                        song[f"{media_type}FileSize"] = s3_head.get("ContentLength")
                        song[f"{media_type}FileType"] = s3_head.get("ContentType")
                        song[f"{media_type}LastModified"] = s3_head.get("LastModified").isoformat()
                        song[f"{media_type}Url"] = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
                    except Exception:
                        pass

            songs_data.append(song)

        return create_response(200, {"data": songs_data})

    except Exception as e:
        return create_response(500, {"message": str(e)})
