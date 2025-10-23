import json
import os
import boto3
from utils.utils import create_response

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

transcriptions_table = dynamodb.Table(os.environ['TRANSCRIPTIONS_TABLE'])

def handler(event, context):
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            song_id = key.split('/')[-1].replace('.json', '')

            obj = s3.get_object(Bucket=bucket, Key=key)
            data = json.loads(obj['Body'].read())

            transcript = data['results']['transcripts'][0]['transcript']

            transcriptions_table.put_item(
                Item={
                    'song_id': song_id,
                    'lyrics': transcript
                }
            )

        return create_response(200, {"message": "Lyrics saved to transcriptions table."})

    except Exception as e:
        return create_response(500, {"error": str(e)})
