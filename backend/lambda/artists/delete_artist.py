import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])
artist_catalog_table = dynamodb.Table(os.environ["ARTIST_CATALOG_TABLE"])

def _delete_all_edges_for_artist(artist_id):
    resp = genre_catalog_table.query(
        IndexName="BySongIndex",
        KeyConditionExpression=Key('SK').eq(f'ARTIST#{artist_id}'),
        ProjectionExpression='PK, SK'
    )
    items = resp.get('Items', [])
    while 'LastEvaluatedKey' in resp:
        resp = genre_catalog_table.query(
            IndexName="BySongIndex",
            KeyConditionExpression=Key('SK').eq(f'ARTIST#{artist_id}'),
            ProjectionExpression='PK, SK',
            ExclusiveStartKey=resp['LastEvaluatedKey']
        )
        items.extend(resp.get('Items', []))

    if items:
        with genre_catalog_table.batch_writer() as batch:
            for it in items:
                batch.delete_item(Key={'PK': it['PK'], 'SK': it['SK']})

    resp = artist_catalog_table.query(
        KeyConditionExpression=Key('PK').eq(f'ARTIST#{artist_id}'),
        ProjectionExpression='PK, SK'
    )
    items = resp.get('Items', [])

    while 'LastEvaluatedKey' in resp:
        resp = artist_catalog_table.query(
            KeyConditionExpression=Key('PK').eq(f'ARTIST#{artist_id}'),
            ProjectionExpression='PK, SK',
            ExclusiveStartKey=resp['LastEvaluatedKey']
        )
        items.extend(resp.get('Items', []))

    if items:
        with artist_catalog_table.batch_writer() as batch:
            for it in items:
                batch.delete_item(Key={'PK': it['PK'], 'SK': it['SK']})

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

        _delete_all_edges_for_artist(artist_id)
        artists_table.delete_item(Key={'id': artist_id, 'name': name})

        return create_response(200, {"message": resp})
        
    except Exception as e:
        return create_response(500, {"message": str(e)})
