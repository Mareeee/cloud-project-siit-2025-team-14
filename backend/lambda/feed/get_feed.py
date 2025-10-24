import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
bucket_name = os.environ["MEDIA_BUCKET"]

feed_table    = dynamodb.Table(os.environ["FEED_TABLE"])
songs_table   = dynamodb.Table(os.environ["SONGS_TABLE"])
albums_table  = dynamodb.Table(os.environ["ALBUMS_TABLE"])
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])

def _is_evening(ts_iso: str) -> bool:
    try:
        ts_iso = ts_iso.replace('Z', '+00:00') if ts_iso.endswith('Z') else ts_iso
        dt = datetime.fromisoformat(ts_iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt_local = dt.astimezone(ZoneInfo("Europe/Belgrade"))
        return dt_local.hour >= 20 or dt_local.hour < 3
    except Exception:
        return False

def handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        user_id = params.get("userId")
        if not user_id:
            return create_response(400, {"message": "Missing userId."})

        response = feed_table.query(
            KeyConditionExpression=Key("userId").eq(user_id),
            ScanIndexForward=False
        )
        items = response.get("Items", [])

        grouped = defaultdict(lambda: {"score": 0, "type": None})
        for it in items:
            cid = it.get("contentId")
            t   = it.get("type")
            if not cid or not t:
                continue
            grouped[(cid, t)]["type"]  = t
            grouped[(cid, t)]["score"] += int(it.get("score", 0))

            if (
                t == "SONG"
                and (it.get("reason") or "").lower() == "listening activity"
                and it.get("timestamp")
                and _is_evening(it["timestamp"])
            ):
                grouped[(cid, t)]["score"] += 1

        songs_map, albums_map, artists_map = defaultdict(int), defaultdict(int), defaultdict(int)
        for (cid, t), data in grouped.items():
            if t == "SONG":
                songs_map[cid] += data["score"]
            elif t == "ALBUM":
                albums_map[cid] += data["score"]
            elif t in ("ARTIST", "META"):
                artists_map[cid] += data["score"]

        songs_sorted   = sorted(songs_map.items(),   key=lambda kv: kv[1], reverse=True)
        albums_sorted  = sorted(albums_map.items(),  key=lambda kv: kv[1], reverse=True)
        artists_sorted = sorted(artists_map.items(), key=lambda kv: kv[1], reverse=True)

        seen_songs, seen_albums, seen_artists = set(), set(), set()
        songs_feed   = _fetch_by_ids(songs_sorted,   songs_table,   "SongIdIndex",   "SONG",   12, seen_songs)
        albums_feed  = _fetch_by_ids(albums_sorted,  albums_table,  "AlbumIdIndex",  "ALBUM",  12, seen_albums)
        artists_feed = _fetch_by_ids(artists_sorted, artists_table, "ArtistIdIndex", "ARTIST", 12, seen_artists)

        result = {
            "songs":   songs_feed[:12],
            "albums":  albums_feed[:12],
            "artists": artists_feed[:12],
        }
        return create_response(200, {"feed": result})

    except Exception as e:
        print("Error:", e)
        return create_response(500, {"message": str(e)})

def _fetch_by_ids(sorted_pairs, table, index_name, t, limit, seen_ids):
    out = []
    for cid, score in sorted_pairs:
        if len(out) >= limit:
            break
        if not cid or cid in seen_ids:
            continue
        ent = _fetch_entity(table, index_name, cid, t)
        if not ent:
            continue
        seen_ids.add(cid)
        out.append({"type": t, "score": score, t.lower(): ent})
    return out

def _fetch_entity(table, index_name, cid, t):
    try:
        resp = table.query(IndexName=index_name, KeyConditionExpression=Key("id").eq(cid))
        items = resp.get("Items")
        if not items:
            return None
        ent = items[0]

        if t == "SONG":
            if ent.get("s3KeyAudio"):
                ent["audioUrl"] = s3.generate_presigned_url(
                    "get_object", Params={"Bucket": bucket_name, "Key": ent["s3KeyAudio"]}, ExpiresIn=600
                )
            if ent.get("s3KeyCover"):
                ent["imageUrl"] = s3.generate_presigned_url(
                    "get_object", Params={"Bucket": bucket_name, "Key": ent["s3KeyCover"]}, ExpiresIn=600
                )
        return ent
    except Exception as e:
        print(f"_fetch_entity {t} error:", e)
        return None
