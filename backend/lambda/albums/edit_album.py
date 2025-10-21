import os
import json
import boto3
import uuid
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])

def _get_or_create_genre(genre_name):
    resp = genres_table.query(
        IndexName="GenreNameIndex",
        KeyConditionExpression=Key("name").eq(genre_name)
    )
    items = resp.get("Items", [])
    if items:
        return {"id": items[0]["id"], "name": items[0]["name"]}
    genre_id = str(uuid.uuid4())
    genres_table.put_item(Item={"id": genre_id, "name": genre_name})
    return {"id": genre_id, "name": genre_name}

def handler(event, context):
    try:
        album_id = event.get("pathParameters", {}).get("albumId")
        if not album_id:
            return create_response(400, {"message": "albumId is required"})

        body = json.loads(event.get("body") or "{}")

        resp = albums_table.query(
            KeyConditionExpression=Key("id").eq(album_id),
            ConsistentRead=True
        )
        items = resp.get("Items", [])
        if not items:
            return create_response(404, {"message": f"Album with id {album_id} not found."})
        album = items[0]

        old_title = album.get("title")
        old_release_date = album.get("releaseDate")
        old_genre_ids = album.get("genreIds", [])
        old_artist_ids = album.get("artistIds", [])

        new_title = body.get("title", old_title)
        new_release_date = body.get("releaseDate", old_release_date)
        new_genres = body.get("genres") or []
        new_artist_ids = body.get("artistIds") or []

        updated_fields = {}
        title_changed = new_title != old_title

        if new_release_date != old_release_date:
            updated_fields["releaseDate"] = new_release_date

        if set(new_artist_ids) != set(old_artist_ids):
            updated_fields["artistIds"] = new_artist_ids

        genre_ids_changed = False
        if new_genres:
            new_genre_data = [_get_or_create_genre(g) for g in new_genres]
            new_genre_ids = [g["id"] for g in new_genre_data]
            if set(new_genre_ids) != set(old_genre_ids):
                updated_fields["genreIds"] = new_genre_ids
                genre_ids_changed = True
        else:
            new_genre_ids = old_genre_ids
            new_genre_data = []

        if not updated_fields and not title_changed:
            return create_response(200, {"message": "No changes detected."})

        if title_changed:
            new_item = album.copy()
            new_item["title"] = new_title
            if "releaseDate" in updated_fields:
                new_item["releaseDate"] = updated_fields["releaseDate"]
            if "artistIds" in updated_fields:
                new_item["artistIds"] = updated_fields["artistIds"]
            if "genreIds" in updated_fields:
                new_item["genreIds"] = updated_fields["genreIds"]

            albums_table.put_item(Item=new_item)
            albums_table.delete_item(Key={"id": album_id, "title": old_title})
        else:
            expr_names, expr_vals, sets = {}, {}, []
            for k, v in updated_fields.items():
                expr_names[f"#{k}"] = k
                expr_vals[f":{k}"] = v
                sets.append(f"#{k} = :{k}")

            if sets:
                albums_table.update_item(
                    Key={"id": album_id, "title": old_title},
                    UpdateExpression="SET " + ", ".join(sets),
                    ExpressionAttributeNames=expr_names,
                    ExpressionAttributeValues=expr_vals
                )

        if genre_ids_changed or title_changed:
            resp = genre_catalog_table.query(
                IndexName="ByAlbumIndex",
                KeyConditionExpression=Key("SK").eq(f"ALBUM#{album_id}")
            )
            items_to_delete = resp.get("Items", [])
            with genre_catalog_table.batch_writer() as batch:
                for it in items_to_delete:
                    batch.delete_item(Key={"PK": it["PK"], "SK": it["SK"]})

            if new_genre_data:
                for g in new_genre_data:
                    genre_catalog_table.put_item(Item={
                        "PK": f"GENRE#{g['name']}",
                        "SK": f"ALBUM#{album_id}",
                        "entityType": "ALBUM",
                        "entityId": album_id,
                        "title": new_title,
                        "releaseDate": new_release_date
                    })

        return create_response(200, {
            "message": "Album updated successfully.",
            "updatedFields": list(updated_fields.keys()) + (["title"] if title_changed else [])
        })

    except Exception as e:
        print("Error updating album:", str(e))
        return create_response(500, {"message": "Edit failed", "error": str(e)})
