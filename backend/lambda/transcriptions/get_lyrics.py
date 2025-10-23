import os
import boto3
from utils.utils import create_response

dynamodb = boto3.resource('dynamodb')
transcriptions_table = dynamodb.Table(os.environ['TRANSCRIPTIONS_TABLE'])

def handler(event, context):
    try:
        song_id = event['pathParameters']['song_id']

        response = transcriptions_table.get_item(Key={'song_id': song_id})
        item = response.get('Item')

        if not item:
            return create_response(200, {"lyrics": None})

        return create_response(200, {"lyrics": item.get('lyrics', None)})

    except Exception as e:
        return create_response(500, {"error": str(e)})
