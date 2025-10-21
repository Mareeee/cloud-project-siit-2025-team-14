import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])

def handler(event, context):
    try:
        artist_id = event["pathParameters"]["artistId"]

        resp = artists_table.query(
            KeyConditionExpression=Key('id').eq(artist_id),
            ProjectionExpression='#n',
            ExpressionAttributeNames={'#n': 'name'},
            ConsistentRead=True
        )

        items = resp.get('Items', [])
        if not items:
            return create_response(404, {"message": "Artist not found"})
        
        item = items[0]
        name = item['name']

        artists_table.delete_item(Key={'id': artist_id, 'name': name})

        return create_response(200, {"message": resp})
        
    except Exception as e:
        return create_response(500, {"message": str(e)})
