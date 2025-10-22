import os
import boto3
import json
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource("dynamodb")
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genres_table  = dynamodb.Table(os.environ["GENRES_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])

def _genre_names_by_ids(ids):
    """Vrati listu naziva žanrova za date ID-jeve (isto kao u edit_song)."""
    names = []
    for gid in ids or []:
        resp = genres_table.query(
            IndexName="GenreIdIndex",
            KeyConditionExpression=Key("id").eq(gid),
            Limit=1
        )
        items = resp.get("Items", [])
        if items:
            names.append(items[0]["name"])
    return names

def handler(event, context):
    try:
        artist_id = event["pathParameters"]["artistId"]
        body = json.loads(event.get("body") or "{}")

        resp = artists_table.query(
            KeyConditionExpression=Key("id").eq(artist_id),
            Limit=1,
            ConsistentRead=True
        )
        items = resp.get("Items", [])
        if not items:
            return create_response(404, {"message": f"Artist with id {artist_id} not found."})

        artist = items[0]
        old_bio       = artist.get("biography")
        old_genre_ids = artist.get("genreIds", [])
        artist_name   = artist.get("name")

        new_bio       = body.get("biography")
        new_genre_ids = body.get("genreIds")

        changed = {}
        if new_bio is not None and new_bio != old_bio:
            changed["biography"] = new_bio
        genres_changed = (new_genre_ids is not None and set(new_genre_ids) != set(old_genre_ids))
        if genres_changed:
            changed["genreIds"] = new_genre_ids

        if not changed:
            return create_response(200, {"message": "No changes detected.", "updated": [], "body": body})

        expr_names, expr_vals, sets = {}, {}, []
        for k, v in changed.items():
            expr_names[f"#{k}"] = k
            expr_vals[f":{k}"] = v
            sets.append(f"#{k} = :{k}")

        artists_table.update_item(
            Key={"id": artist_id, "name": artist_name},
            UpdateExpression="SET " + ", ".join(sets),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_vals
        )

        genre_links = {"added": [], "removed": []}

        if genres_changed:
            existing_items = genre_catalog_table.query(
                IndexName="BySongIndex",
                KeyConditionExpression=Key("SK").eq(f"ARTIST#{artist_id}")
            ).get("Items", [])

            genre_names = _genre_names_by_ids(new_genre_ids)
            new_pks = [f"GENRE#{nm}" for nm in genre_names]
            existing_pks = [it["PK"] for it in existing_items]

            to_add   = list(set(new_pks) - set(existing_pks))
            to_remove= list(set(existing_pks) - set(new_pks))

            for pk in to_add:
                genre_catalog_table.put_item(Item={
                    "PK": pk,
                    "SK": f"ARTIST#{artist_id}",
                    "entityType": "ARTIST",
                    "entityId": artist_id,
                    "name": artist_name,
                    "biography": new_bio if new_bio is not None else old_bio,
                    "genres": genre_names
                })

            for pk in to_remove:
                genre_catalog_table.delete_item(Key={"PK": pk, "SK": f"ARTIST#{artist_id}"})

            genre_links = {"added": to_add, "removed": to_remove}

        return create_response(200, {
            "message": "Artist updated.",
            "id": artist_id,
            "updated": list(changed.keys()),
            "genreLinks": genre_links
        })

    except Exception as e:
        return create_response(500, {"message": str(e)})
