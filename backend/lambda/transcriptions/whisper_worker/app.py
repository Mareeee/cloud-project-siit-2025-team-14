import os
import json
import boto3
import tempfile
import whisper
import time

s3 = boto3.client('s3')

WHISPER_MODEL_DIR = os.path.join(tempfile.gettempdir(), "whisper_models")
os.makedirs(WHISPER_MODEL_DIR, exist_ok=True)
model = whisper.load_model("tiny.en", download_root=WHISPER_MODEL_DIR)


def handler(event, context):
    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            song_id = body['song_id']
            s3_audio_key = body['s3_audio_key']
            bucket = body['bucket']

            local_audio_path = os.path.join(tempfile.gettempdir(), os.path.basename(s3_audio_key))

            s3.download_file(bucket, s3_audio_key, local_audio_path)

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = model.transcribe(local_audio_path, fp16=False)
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    else:
                        raise e

            output_key = f"lyrics/{song_id}.json"
            output_json = json.dumps({
                "results": {
                    "transcripts": [{"transcript": result['text']}]
                }
            })

            s3.put_object(
                Bucket=bucket,
                Key=output_key,
                Body=output_json.encode("utf-8"),
                ContentType="application/json"
            )

        except Exception as e:
            raise e

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Transcription worker finished."})
    }
