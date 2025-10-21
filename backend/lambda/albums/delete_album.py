import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])

def handler(event, context):
    return create_response(200, {"message": "Album deleted successfully."})
