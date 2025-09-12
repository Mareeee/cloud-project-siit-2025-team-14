import os
import boto3
import uuid
import json
from songs.utils.utils import create_response

s3 = boto3.client("s3")
bucket = os.environ["MEDIA_BUCKET"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["SONGS_TABLE"])

def handler(event, context):
    try:
        body = json.loads(event["body"])
        title = body.get("title")
        filename = body.get("filename")

        if not title or not filename:
            return create_response(400, {"message": "title and filename required"})
        
        song_id = str(uuid.uuid4())
        s3_key = f"{song_id}/{filename}"

        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": s3_key},
            ExpiresIn=300
        )

        table.put_item(Item={
            "id": song_id,
            "title": title,
            "s3Key": s3_key
        })

        return create_response(200, {
            "message": f'Song "{title}" ready for upload',
            "id": song_id,
            "uploadUrl": presigned_url
        })
    except Exception as e:
        return create_response(500, {"message": str(e)})
