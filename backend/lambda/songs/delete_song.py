import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

bucket = os.environ["MEDIA_BUCKET"]
songs_table = dynamodb.Table(os.environ["SONGS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
ratings_table = dynamodb.Table(os.environ["RATINGS_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])
artist_catalog_table = dynamodb.Table(os.environ["ARTIST_CATALOG_TABLE"])

def _delete_s3_prefix(bucket_name: str, prefix: str):
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        objects = [{'Key': obj['Key']} for obj in page.get('Contents', [])]
        if objects:
            s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects, 'Quiet': True})

def _delete_all_edges_for_song(song_id: str):
    resp = genre_catalog_table.query(
        IndexName="BySongIndex",
        KeyConditionExpression=Key('SK').eq(f'SONG#{song_id}'),
        ProjectionExpression='PK, SK'
    )
    items = resp.get('Items', [])
    while 'LastEvaluatedKey' in resp:
        resp = genre_catalog_table.query(
            IndexName="BySongIndex",
            KeyConditionExpression=Key('SK').eq(f'SONG#{song_id}'),
            ProjectionExpression='PK, SK',
            ExclusiveStartKey=resp['LastEvaluatedKey']
        )
        items.extend(resp.get('Items', []))

    if items:
        with genre_catalog_table.batch_writer() as batch:
            for it in items:
                batch.delete_item(Key={'PK': it['PK'], 'SK': it['SK']})

    resp = artist_catalog_table.query(
        IndexName="BySongIndex",
        KeyConditionExpression=Key('SK').eq(f'SONG#{song_id}'),
        ProjectionExpression='PK, SK'
    )
    items = resp.get('Items', [])

    while 'LastEvaluatedKey' in resp:
        resp = artist_catalog_table.query(
            IndexName="BySongIndex",
            KeyConditionExpression=Key('SK').eq(f'SONG#{song_id}'),
            ProjectionExpression='PK, SK',
            ExclusiveStartKey=resp['LastEvaluatedKey']
        )
        items.extend(resp.get('Items', []))

    if items:
        with artist_catalog_table.batch_writer() as batch:
            for it in items:
                batch.delete_item(Key={'PK': it['PK'], 'SK': it['SK']})

    resp = ratings_table.query(
        IndexName="BySongIndex",
        KeyConditionExpression=Key("contentId").eq(song_id),
        ProjectionExpression="contentId, userId"
    )
    items = resp.get("Items", [])

    while "LastEvaluatedKey" in resp:
        resp = ratings_table.query(
            IndexName="BySongIndex",
            KeyConditionExpression=Key("contentId").eq(song_id),
            ProjectionExpression="contentId, userId",
            ExclusiveStartKey=resp["LastEvaluatedKey"]
        )
        items.extend(resp.get("Items", []))

    if items:
        with ratings_table.batch_writer() as batch:
            for it in items:
                batch.delete_item(Key={"contentId": it["contentId"], "userId": it["userId"]})

def handler(event, context):
    try:
        song_id = event["pathParameters"]["songId"]

        resp = songs_table.query(
            KeyConditionExpression=Key('id').eq(song_id),
            ProjectionExpression='#t, s3KeyAudio, s3KeyCover',
            ExpressionAttributeNames={'#t': 'title'},
            ConsistentRead=True
        )

        items = resp.get('Items', [])
        if not items:
            return create_response(404, {"message": "Song not found"})
        
        item = items[0]
        title = item['title']

        _delete_s3_prefix(bucket, f"{song_id}/")

        songs_table.delete_item(Key={'id': song_id, 'title': title})

        _delete_all_edges_for_song(song_id)

        return create_response(200, {"message": True})
        
    except Exception as e:
        return create_response(500, {"message": str(e)})
