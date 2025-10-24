import boto3
import uuid
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")

def clear_genres_table():
    table = dynamodb.Table("GenresTable")
    scan = table.scan()
    with table.batch_writer() as batch:
        for item in scan.get("Items", []):
            if "id" in item and "name" in item:
                batch.delete_item(Key={"id": item["id"], "name": item["name"]})


def handler(event, context):
    try:
        if event.get("reset", True):
            clear_genres_table()

        genres_table = dynamodb.Table("GenresTable")

        genres = [
            {"id": str(uuid.uuid4()), "name": "Rock"},
            {"id": str(uuid.uuid4()), "name": "Pop"},
            {"id": str(uuid.uuid4()), "name": "Jazz"},
            {"id": str(uuid.uuid4()), "name": "Hip-Hop"},
            {"id": str(uuid.uuid4()), "name": "Classical"},
        ]

        for g in genres:
            genres_table.put_item(Item=g)

        return create_response(200, {
            "message": "Genres seeded successfully!",
            "count": len(genres)
        })

    except Exception as e:
        return create_response(500, {"message": str(e)})