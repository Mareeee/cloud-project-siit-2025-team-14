import os
import json
import boto3
from presign.utils.utils import create_response

s3 = boto3.client("s3")
bucket = os.environ["MEDIA_BUCKET"]

def handler(event, context):
    try:
        query = event.get("queryStringParameters") or {}
        filename = query.get("filename")
        if not filename:
            return create_response(400, {"message": "filename is required"})

        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": filename},
            ExpiresIn=600
        )

        return create_response(200, {"uploadUrl": presigned_url})
    except Exception as e:
        return create_response(500, {"message": str(e)})
