import os
import boto3
import uuid
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

s3 = boto3.client("s3")
bucket = os.environ["MEDIA_BUCKET"]
dynamodb = boto3.resource("dynamodb")

songs_table = dynamodb.Table(os.environ["SONGS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])
artist_catalog_table = dynamodb.Table(os.environ["ARTIST_CATALOG_TABLE"])

def handler(event, context):
    song_id = event["pathParameters"]["id"]

    # songs_table.delete_item(Key={'id': song_id})
    return {"statusCode": 204}