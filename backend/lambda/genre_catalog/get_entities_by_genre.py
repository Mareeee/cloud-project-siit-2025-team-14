import os
import boto3
from boto3.dynamodb.conditions import Key
from songs.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])

def handler(event, context):
    try:
        genre = event["pathParameters"].get("genre")
        if not genre:
            return create_response(400, {"message": "Genre parameter required."})

        response = genre_catalog_table.query(
            KeyConditionExpression=Key("PK").eq(f"GENRE#{genre}")
        )

        items = response.get("Items", [])
        return create_response(200, {"data": items})

    except Exception as e:
        return create_response(500, {"message": str(e)})
