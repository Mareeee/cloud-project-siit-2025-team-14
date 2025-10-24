import os
import json
import boto3
import time
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb")
feed_table = dynamodb.Table(os.environ["FEED_TABLE"])
songs_table = dynamodb.Table(os.environ["SONGS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
subscriptions_table = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])
genre_catalog_table = dynamodb.Table(os.environ["GENRE_CATALOG_TABLE"])

def handler(event, context):
    try:
        for record in event["Records"]:
            message = json.loads(record["body"])
            msg = json.loads(message.get("Message", "{}"))
            event_type = msg.get("eventType")

            if event_type == "song_uploaded":
                process_song_uploaded(msg)
            elif event_type == "song_listened":
                process_listened_song(msg)
            elif event_type == "user_rated":
                process_user_rated(msg)
            elif event_type == "user_subscribed":
                process_user_subscribed(msg)
            elif event_type == "user_unsubscribed":
                process_user_unsubscribed(msg)
            elif event_type == "rating_deleted":
                process_user_unrate(msg)

        return {"statusCode": 200}
    except Exception as e:
        print("Error:", e)
        return {"statusCode": 500, "body": str(e)}

def process_song_uploaded(msg):
    song_id = msg.get("songId")
    title = msg.get("title")
    artist_ids = msg.get("artistIds", [])
    genres = msg.get("genres", [])
    timestamp = msg.get("timestamp") or datetime.utcnow().isoformat()

    targets = [(gid, "GENRE", 5) for gid in genres] + [(aid, "ARTIST", 8) for aid in artist_ids]

    for target_id, target_type, base_score in targets:
        response = subscriptions_table.query(
            IndexName="targetId-index",
            KeyConditionExpression=Key("targetId").eq(target_id)
        )
        for item in response.get("Items", []):
            user_id = item["userId"]
            feed_table.put_item(Item={
                "userId": user_id,
                "createdAt": str(int(time.time() * 1000)),
                "type": "SONG",
                "contentId": song_id,
                "title": title,
                "reason": f"New for your {target_type.lower()}: {target_id}",
                "timestamp": timestamp,
                "score": base_score,
            })

def process_user_unrate(msg):
    user_id = msg.get("userId")
    content_id = msg.get("contentId")
    if not user_id or not content_id:
        print("process_user_unrate: missing userId/contentId", msg)
        return

    last_key = None
    deleted = 0
    while True:
        q = {
            "KeyConditionExpression": Key("userId").eq(user_id),
            "ScanIndexForward": False,
            "Limit": 100,
            "FilterExpression": Attr("contentId").eq(content_id),
        }
        if last_key:
            q["ExclusiveStartKey"] = last_key

        resp = feed_table.query(**q)
        items = resp.get("Items", [])
        for it in items:
            feed_table.delete_item(Key={"userId": user_id, "createdAt": it["createdAt"]})
            deleted += 1

        last_key = resp.get("LastEvaluatedKey")
        if not last_key:
            break

    print(f"process_user_unrate: deleted {deleted} items for user={user_id} content={content_id}")

def process_user_rated(msg):
    user_id = msg.get("userId")
    content_id = msg.get("contentId")
    rating = msg.get("rating")

    if not user_id or not content_id:
        print("process_user_rated: missing userId/contentId", msg)
        return

    last_key = None
    while True:
        q = {
            "KeyConditionExpression": Key("userId").eq(user_id),
            "ScanIndexForward": False,
            "Limit": 100,
            "FilterExpression": Attr("contentId").eq(content_id),
        }
        if last_key:
            q["ExclusiveStartKey"] = last_key
        resp = feed_table.query(**q)
        for it in resp.get("Items", []):
            feed_table.delete_item(Key={"userId": user_id, "createdAt": it["createdAt"]})
        if not resp.get("LastEvaluatedKey"):
            break

    try:
        r = int(rating) if rating else 0
    except Exception:
        r = 0
    if r <= 0:
        return

    feed_table.put_item(Item={
        "userId": user_id,
        "createdAt": str(int(time.time() * 1000)),
        "type": "SONG",
        "contentId": content_id,
        "reason": f"Rated song {r}★",
        "timestamp": datetime.utcnow().isoformat(),
        "score": r * 4,
    })

def process_user_subscribed(msg):
    user_id = msg.get("userId")
    target_id = msg.get("targetId")
    raw_type = msg.get("targetType", "")
    target_type = str(raw_type).upper()
    base_score = 3 if target_type == "GENRE" else 4

    feed_table.put_item(Item={
        "userId": user_id,
        "createdAt": str(int(time.time() * 1000)),
        "type": "META",
        "contentId": target_id,
        "reason": f"Subscription to {target_type.lower()} {target_id}",
        "timestamp": datetime.utcnow().isoformat(),
        "score": base_score,
    })

    if target_type == "GENRE":
        try:
            response = genres_table.query(
                IndexName="GenreIdIndex",
                KeyConditionExpression=Key("id").eq(target_id)
            )
            genres = response.get("Items", [])

            _hydrate_feed_from_genre(user_id, genres[0].get("name"))
        except Exception as e:
            print("hydrate_from_genre error:", e)

def process_user_unsubscribed(msg):
    user_id  = msg.get("userId")
    genre_id = msg.get("targetId")

    if not user_id or not genre_id:
        print("process_user_unsubscribed: missing userId/genreId", msg)
        return

    last_key = None
    while True:
        q = {
            "KeyConditionExpression": Key("userId").eq(user_id),
            "ScanIndexForward": False,
            "FilterExpression": Attr("contentId").eq(genre_id) & Attr("type").eq("META"),
            "Limit": 100,
        }
        if last_key:
            q["ExclusiveStartKey"] = last_key

        resp = feed_table.query(**q)
        for it in resp.get("Items", []):
            feed_table.delete_item(Key={"userId": user_id, "createdAt": it["createdAt"]})
        if not resp.get("LastEvaluatedKey"):
            break

    try:
        gresp = genres_table.query(
            IndexName="GenreIdIndex",
            KeyConditionExpression=Key("id").eq(genre_id)
        )
        gitems = gresp.get("Items", [])
        if not gitems:
            print("process_user_unsubscribed: genre not found for id", genre_id)
            _delete_by_reason_contains(user_id, str(genre_id))
            return

        genre_name = gitems[0].get("name")
    except Exception as e:
        print("process_user_unsubscribed: failed to resolve genre name:", e)
        _delete_by_reason_contains(user_id, str(genre_id))
        return

    try:
        resp = genre_catalog_table.query(
            KeyConditionExpression=Key("PK").eq(f"GENRE#{genre_name}")
        )
        items = resp.get("Items", [])

        for it in items:
            etype = (it.get("entityType") or "").upper()
            content_id = (it.get("songId") or it.get("albumId") or
                          it.get("artistId") or it.get("id") or it.get("entityId"))
            if not etype or not content_id:
                continue
            _delete_existing_feed_entries(user_id, content_id, etype)
    except Exception as e:
        print("process_user_unsubscribed: delete hydrated items error:", e)

    _delete_by_reason_contains(user_id, str(genre_id))

def _hydrate_feed_from_genre(user_id, genre_name):
    SCORE_BY_TYPE = {"SONG": 4, "ALBUM": 3, "ARTIST": 2}
    MAX_ITEMS = 50

    resp = genre_catalog_table.query(
        KeyConditionExpression=Key("PK").eq(f"GENRE#{genre_name}")
    )
    items = resp.get("Items", [])[:MAX_ITEMS]

    for it in items:
        now_iso = datetime.utcnow().isoformat()
        now_ms  = str(int(time.time() * 1000))

        etype = (it.get("entityType") or "").upper()
        if etype not in SCORE_BY_TYPE:
            continue

        content_id = it.get("songId") or it.get("albumId") or it.get("artistId") or it.get("id") or it.get("entityId")
        if not content_id:
            continue

        _delete_existing_feed_entries(user_id, content_id, etype)

        feed_table.put_item(Item={
            "userId": user_id,
            "createdAt": now_ms,
            "type": etype,
            "contentId": content_id,
            "reason": f"Connected by genre: {genre_name}",
            "timestamp": now_iso,
            "score": SCORE_BY_TYPE[etype],
        })

def _delete_by_reason_contains(user_id, needle):
    last_key = None
    deleted = 0
    while True:
        q = {
            "KeyConditionExpression": Key("userId").eq(user_id),
            "ScanIndexForward": False,
            "Limit": 100,
            "FilterExpression": Attr("reason").contains(needle),
        }
        if last_key:
            q["ExclusiveStartKey"] = last_key

        resp = feed_table.query(**q)
        for it in resp.get("Items", []):
            feed_table.delete_item(Key={"userId": user_id, "createdAt": it["createdAt"]})
            deleted += 1

        last_key = resp.get("LastEvaluatedKey")
        if not last_key:
            break

    print(f"_delete_by_reason_contains: deleted {deleted} items for user={user_id} reason~={needle}")

def _delete_existing_feed_entries(user_id, content_id, t):
    last_key = None
    while True:
        q = {
            "KeyConditionExpression": Key("userId").eq(user_id),
            "ScanIndexForward": False,
            "Limit": 100,
            "FilterExpression": Attr("contentId").eq(content_id) & Attr("type").eq(t),
        }
        if last_key:
            q["ExclusiveStartKey"] = last_key
        resp = feed_table.query(**q)
        for it in resp.get("Items", []):
            feed_table.delete_item(Key={"userId": user_id, "createdAt": it["createdAt"]})
        last_key = resp.get("LastEvaluatedKey")
        if not last_key:
            break

def process_listened_song(msg):
    user_id = msg.get("userId")
    song_id = msg.get("songId")

    if not user_id or not song_id:
        print("process_listened_song: missing userId/songId", msg)
        return

    resp = feed_table.query(
        KeyConditionExpression=Key("userId").eq(user_id),
        ScanIndexForward=False,
        Limit=1,
        FilterExpression=Attr("contentId").eq(song_id) & Attr("type").eq("SONG"),
    )

    items = resp.get("Items", [])
    now_iso = datetime.utcnow().isoformat()
    now_ms = str(int(time.time() * 1000))

    if not items:
        feed_table.put_item(Item={
            "userId": user_id,
            "createdAt": now_ms,
            "type": "SONG",
            "contentId": song_id,
            "reason": "Listening activity",
            "timestamp": now_iso,
            "score": 1,
        })
        print(f"process_listened_song: added new song {song_id} to feed for user {user_id}")
    else:
        item = items[0]
        new_score = item.get("score", 0) + 1

        feed_table.update_item(
            Key={"userId": user_id, "createdAt": item["createdAt"]},
            UpdateExpression="SET #s = :s, #t = :t",
            ExpressionAttributeNames={"#s": "score", "#t": "timestamp"},
            ExpressionAttributeValues={":s": new_score, ":t": now_iso}
        )
        print(f"process_listened_song: updated score for {song_id}, new score={new_score}")
