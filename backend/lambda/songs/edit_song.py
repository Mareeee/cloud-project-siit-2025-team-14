import os
import json
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

BUCKET = os.environ["MEDIA_BUCKET"]
songs_table         = dynamodb.Table(os.environ["SONGS_TABLE"])
genres_table        = dynamodb.Table(os.environ["GENRES_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])
artist_catalog_table = dynamodb.Table(os.environ["ARTIST_CATALOG_TABLE"])

def _is_url(s: str) -> bool:
    return isinstance(s, str) and (s.startswith("http://") or s.startswith("https://") or s.startswith("s3://"))

def _set_diff(old_list, new_list):
    old, new = set(old_list or []), set(new_list or [])
    return list(new - old), list(old - new)

def _genre_names_by_ids(ids):
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

def _safe_delete_object(bucket: str, key: str):
    try:
        if key:
            s3.delete_object(Bucket=bucket, Key=key)
    except Exception:
        pass

def handler(event, context):
    song_id = str(event["pathParameters"]["songId"]).strip()

    try:
        q = songs_table.query(
            IndexName="SongIdIndex",
            KeyConditionExpression=Key("id").eq(song_id)
        )
        items = q.get("Items", [])
        if not items:
            return create_response(404, {"message": f"Song with id {song_id} not found."})
        song = items[0]

        body = json.loads(event.get("body") or "{}")

        old_title     = song.get("title")
        old_album_id  = song.get("albumId")
        old_artists   = song.get("artistIds")
        old_genres    = song.get("genreIds") or []
        old_cover_key = song.get("s3KeyCover")
        old_audio_key = song.get("s3KeyAudio")
        creation_date = song.get("creationDate")

        new_album_id  = body.get("albumId")
        new_artists   = body.get("artistIds")
        new_genres    = body.get("genreIds") or body.get("genres")
        cover_in      = body.get("coverFilename")
        audio_in      = body.get("audioFilename")

        cover_changed = bool(cover_in) and not _is_url(cover_in)
        audio_changed = bool(audio_in) and not _is_url(audio_in)

        changed = {}
        if new_album_id is not None and new_album_id != old_album_id:
            changed["albumId"] = new_album_id
        artists_changed = (new_artists is not None and new_artists != old_artists)
        if artists_changed:
            changed["artistIds"] = new_artists
        genres_changed = (new_genres is not None and new_genres != old_genres)
        if genres_changed:
            changed["genreIds"] = new_genres
        genre_names = _genre_names_by_ids(new_genres if genres_changed else old_genres)
        new_cover_key = old_cover_key
        new_audio_key = old_audio_key
        if cover_changed:
            new_cover_key = f"{song_id}/cover/{cover_in.strip()}"
            changed["s3KeyCover"] = new_cover_key
        if audio_changed:
            new_audio_key = f"{song_id}/audio/{audio_in.strip()}"
            changed["s3KeyAudio"] = new_audio_key

        if not changed and not cover_changed and not audio_changed:
            return create_response(200, {"message": "No changes.", "updated": []})

        if changed:
            expr_names, expr_vals, sets = {}, {}, []
            for k, v in changed.items():
                expr_names[f"#{k}"] = k
                expr_vals[f":{k}"] = v
                sets.append(f"#{k} = :{k}")
            songs_table.update_item(
                Key={"id": song_id, "title": old_title},
                UpdateExpression="SET " + ", ".join(sets),
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_vals
            )

        genre_links = {"added": [], "removed": []}
        if genres_changed or cover_changed or audio_changed:
            existing_items = genre_catalog_table.query(
                IndexName="BySongIndex",
                KeyConditionExpression=Key("SK").eq(f"SONG#{song_id}")
            ).get("Items", [])

            if genres_changed:
                genre_names = _genre_names_by_ids(new_genres)
                new_pks = [f"GENRE#{nm}" for nm in genre_names]
                existing_pks = [it["PK"] for it in existing_items]

                to_add, to_remove = _set_diff(existing_pks, new_pks)

                for pk in to_add:
                    genre_catalog_table.put_item(Item={
                        "PK": pk,
                        "SK": f"SONG#{song_id}",
                        "entityType": "SONG",
                        "entityId": song_id,
                        "title": old_title,
                        "creationDate": creation_date,
                        "s3KeyCover": new_cover_key,
                        "s3KeyAudio": new_audio_key,
                        "genres": genre_names
                    })
                for pk in to_remove:
                    genre_catalog_table.delete_item(Key={"PK": pk, "SK": f"SONG#{song_id}"})

                genre_links = {"added": to_add, "removed": to_remove}

                still_existing = [pk for pk in new_pks if pk not in to_add]
                for pk in still_existing:
                    genre_catalog_table.update_item(
                        Key={"PK": pk, "SK": f"SONG#{song_id}"},
                        UpdateExpression="SET #c=:c, #a=:a",
                        ExpressionAttributeNames={"#c": "s3KeyCover", "#a": "s3KeyAudio"},
                        ExpressionAttributeValues={":c": new_cover_key, ":a": new_audio_key}
                    )
            else:
                for it in existing_items:
                    genre_catalog_table.update_item(
                        Key={"PK": it["PK"], "SK": it["SK"]},
                        UpdateExpression="SET #c=:c, #a=:a",
                        ExpressionAttributeNames={"#c": "s3KeyCover", "#a": "s3KeyAudio"},
                        ExpressionAttributeValues={":c": new_cover_key, ":a": new_audio_key}
                    )

        artist_links = {"added": [], "removed": []}
        if artists_changed or cover_changed or audio_changed:
            existing_artist_items = artist_catalog_table.query(
                IndexName="BySongIndex",
                KeyConditionExpression=Key("SK").eq(f"SONG#{song_id}")
            ).get("Items", [])

            if artists_changed:
                new_artist_pks = [f"ARTIST#{aid}" for aid in (new_artists or [])]
                existing_artist_pks = [it["PK"] for it in existing_artist_items]

                to_add_a, to_remove_a = _set_diff(existing_artist_pks, new_artist_pks)

                for pk in to_add_a:
                    artist_catalog_table.put_item(Item={
                        "PK": pk,
                        "SK": f"SONG#{song_id}",
                        "entityType": "SONG",
                        "entityId": song_id,
                        "title": old_title,
                        "creationDate": creation_date,
                        "s3KeyCover": new_cover_key,
                        "s3KeyAudio": new_audio_key,
                        "genres": genre_names
                    })
                for pk in to_remove_a:
                    artist_catalog_table.delete_item(Key={"PK": pk, "SK": f"SONG#{song_id}"})

                artist_links = {"added": to_add_a, "removed": to_remove_a}

                still_existing_a = [pk for pk in new_artist_pks if pk not in to_add_a]
                for pk in still_existing_a:
                    artist_catalog_table.update_item(
                        Key={"PK": pk, "SK": f"SONG#{song_id}"},
                        UpdateExpression="SET #c=:c, #a=:a",
                        ExpressionAttributeNames={"#c": "s3KeyCover", "#a": "s3KeyAudio"},
                        ExpressionAttributeValues={":c": new_cover_key, ":a": new_audio_key}
                    )
            else:
                for it in existing_artist_items:
                    artist_catalog_table.update_item(
                        Key={"PK": it["PK"], "SK": it["SK"]},
                        UpdateExpression="SET #c=:c, #a=:a",
                        ExpressionAttributeNames={"#c": "s3KeyCover", "#a": "s3KeyAudio"},
                        ExpressionAttributeValues={":c": new_cover_key, ":a": new_audio_key}
                    )

        if cover_changed and old_cover_key and old_cover_key != new_cover_key:
            _safe_delete_object(BUCKET, old_cover_key)
        if audio_changed and old_audio_key and old_audio_key != new_audio_key:
            _safe_delete_object(BUCKET, old_audio_key)

        cover_upload_url = None
        audio_upload_url = None
        if cover_changed:
            cover_upload_url = s3.generate_presigned_url(
                "put_object",
                Params={"Bucket": BUCKET, "Key": new_cover_key},
                ExpiresIn=300
            )
        if audio_changed:
            audio_upload_url = s3.generate_presigned_url(
                "put_object",
                Params={"Bucket": BUCKET, "Key": new_audio_key},
                ExpiresIn=300
            )

        return create_response(200, {
            "message": "Song updated.",
            "id": song_id,
            "updated": list(changed.keys()),
            "genreLinks": genre_links,
            "artistLinks": artist_links,
            "coverUploadUrl": cover_upload_url,
            "audioUploadUrl": audio_upload_url
        })

    except Exception as e:
        return create_response(500, {"message": "Edit failed", "error": str(e)})
