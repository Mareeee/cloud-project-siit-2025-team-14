import json
from transcription.utils.utils import create_response

def handler(event, context):
    try:
        for record in event.get("Records", []):
            body = json.loads(record["body"])
            print(f"Processing transcription job for file: {body}")

        return create_response(200, {"message": "Transcription jobs processed successfully."})
    except Exception as e:
        return create_response(500, {"message": str(e)})
