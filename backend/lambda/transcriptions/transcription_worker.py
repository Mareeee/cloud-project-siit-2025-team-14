import json
import boto3
from utils.utils import create_response

transcribe = boto3.client('transcribe')

def handler(event, context):
    try:
        for record in event['Records']:
            body = json.loads(record['body'])
            song_id = body['song_id']
            s3_audio_key = body['s3_audio_key']
            bucket = body['bucket']

            job_name = f"transcribe-{song_id}"
            media_uri = f"s3://{bucket}/{s3_audio_key}"

            transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': media_uri},
                MediaFormat='mp3',
                LanguageCode='en-US',
                OutputBucketName=bucket,
                OutputKey=f"lyrics/{song_id}.json"
            )

        return create_response(200, {"message": "Transcription job started."})

    except Exception as e:
        return create_response(500, {"error": str(e)})
