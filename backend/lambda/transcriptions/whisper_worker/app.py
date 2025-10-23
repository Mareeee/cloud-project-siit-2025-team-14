import os
import json
import boto3
import tempfile
import whisper

s3 = boto3.client('s3')
model = whisper.load_model("base")

def handler(event, context):
    try:
        for record in event['Records']:
            body = json.loads(record['body'])
            song_id = body['song_id']
            s3_audio_key = body['s3_audio_key']
            bucket = body['bucket']

            local_audio_path = os.path.join(tempfile.gettempdir(), os.path.basename(s3_audio_key))
            s3.download_file(bucket, s3_audio_key, local_audio_path)

            result = model.transcribe(local_audio_path, fp16=False)

            output_key = f"lyrics/{song_id}.json"
            output_json = json.dumps({"results": {"transcripts": [{"transcript": result['text']}]}})

            s3.put_object(
                Bucket=bucket,
                Key=output_key,
                Body=output_json.encode("utf-8"),
                ContentType="application/json"
            )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Whisper transcription complete."})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
