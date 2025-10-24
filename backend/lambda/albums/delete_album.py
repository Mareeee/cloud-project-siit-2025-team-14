import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")

albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])

def _delete_all_edges_for_album(album_id: str):
    resp = genre_catalog_table.query(
        IndexName="ByAlbumIndex",
        KeyConditionExpression=Key("SK").eq(f"ALBUM#{album_id}"),
        ProjectionExpression="PK, SK"
    )
    items = resp.get("Items", [])

    while "LastEvaluatedKey" in resp:
        resp = genre_catalog_table.query(
            IndexName="ByAlbumIndex",
            KeyConditionExpression=Key("SK").eq(f"ALBUM#{album_id}"),
            ProjectionExpression="PK, SK",
            ExclusiveStartKey=resp["LastEvaluatedKey"]
        )
        items.extend(resp.get("Items", []))

    if not items:
        print("No related genre catalog entries found for this album.")
        return

    with genre_catalog_table.batch_writer() as batch:
        for it in items:
            batch.delete_item(Key={"PK": it["PK"], "SK": it["SK"]})

def handler(event, context):
    try:
        album_id = event.get("pathParameters", {}).get("albumId")
        if not album_id:
            return create_response(400, {"message": "albumId is required in path parameters"})

        resp = albums_table.query(
            KeyConditionExpression=Key("id").eq(album_id),
            ProjectionExpression="#t",
            ExpressionAttributeNames={"#t": "title"},
            ConsistentRead=True
        )

        items = resp.get("Items", [])
        if not items:
            return create_response(404, {"message": "Album not found"})

        album_title = items[0]["title"]

        albums_table.delete_item(Key={"id": album_id, "title": album_title})

        _delete_all_edges_for_album(album_id)

        return create_response(200, {"message": True})

    except Exception as e:
        print("Error while deleting album:", str(e))
        return create_response(500, {"message": str(e)})
