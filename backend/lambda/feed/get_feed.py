import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response
from collections import defaultdict

dynamodb = boto3.resource("dynamodb")
feed_table = dynamodb.Table(os.environ["FEED_TABLE"])
songs_table = dynamodb.Table(os.environ["SONGS_TABLE"])
albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])

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
            t = it.get("type")
            s = int(it.get("score", 0))
            if not cid or not t:
                continue
            grouped[(cid, t)]["score"] += s
            grouped[(cid, t)]["type"] = t

        sorted_groups = sorted(grouped.items(), key=lambda kv: kv[1]["score"], reverse=True)

        feed_items = []
        for (cid, t), data in sorted_groups:
            item = {"type": t, "score": data["score"]}

            if t == "SONG":
                resp = songs_table.query(
                    IndexName="SongIdIndex",
                    KeyConditionExpression=Key("id").eq(cid)
                )
                song = resp.get("Items", [{}])[0] if resp.get("Items") else None
                if not song:
                    continue
                item["song"] = song

            elif t == "ALBUM":
                resp = albums_table.query(
                    IndexName="AlbumIdIndex",
                    KeyConditionExpression=Key("id").eq(cid)
                )
                album = resp.get("Items", [{}])[0] if resp.get("Items") else None
                if not album:
                    continue
                item["album"] = album

            elif t == "ARTIST":
                resp = artists_table.query(
                    IndexName="ArtistIdIndex",
                    KeyConditionExpression=Key("id").eq(cid)
                )
                artist = resp.get("Items", [{}])[0] if resp.get("Items") else None
                if not artist:
                    continue
                item["artist"] = artist

            elif t == "META":
                resp = artists_table.query(
                    IndexName="ArtistIdIndex",
                    KeyConditionExpression=Key("id").eq(cid)
                )
                artist = resp.get("Items", [{}])[0] if resp.get("Items") else None
                if artist:
                    item["type"] = "ARTIST"
                    item["artist"] = artist
                else:
                    continue
            else:
                continue

            feed_items.append(item)

        return create_response(200, {"feed": feed_items})

    except Exception as e:
        print("Error:", e)
        return create_response(500, {"message": str(e)})
