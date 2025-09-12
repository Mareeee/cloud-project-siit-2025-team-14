import json
import os
import boto3
import uuid

table_name = os.environ['SONGS_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def handler(event, context):
    http_method = event.get("httpMethod")
    if http_method == "OPTIONS":
        return create_response(200, {"message": "CORS preflight"})
    elif http_method == "GET":
        return get_all(event, context)
    elif http_method == "POST":
        return create_song(event, context)
    else:
        return create_response(405, {"message": "Method Not Allowed"})


def get_all(event, context):
    print(event)
    print(context)
    print("hello world log")
    body = {
        'message': 'Hello World from the songs lambda!',
        'data': ['song1', 'song2', 'song3']
    }

    return create_response(200, body)

def create_song(event, context):
    try:
        body = json.loads(event['body'])
        song_id = str(uuid.uuid4())
        name = body.get('name')

        if not song_id or not name:
            return create_response(400, {'message': 'id and name are required'})

        table.put_item(
            Item={
                'id': song_id,
                'title': name
            }
        )

        return create_response(200, {'message': f'Song "{name}" added'})
    except Exception as e:
        return create_response(500, {'message': str(e)})
    

def create_response(status, body):
    return { 
        'statusCode': status, 
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        },
        'body': json.dumps(body, default=str)
    }