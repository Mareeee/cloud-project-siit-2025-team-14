import os
import boto3
from songs.utils.utils import create_response

table_name = os.environ['SONGS_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def handler(event, context):
    try:
        songs = ['song1', 'song2', 'song3']
        return create_response(200, {'data': songs})
    except Exception as e:
        return create_response(500, {'message': str(e)})
