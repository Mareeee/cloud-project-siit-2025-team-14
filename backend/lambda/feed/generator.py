import os
import json
import boto3
import time
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb")
feed_table = dynamodb.Table(os.environ["FEED_TABLE"])
songs_table = dynamodb.Table(os.environ["SONGS_TABLE"])
subscriptions_table = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])

def handler(event, context):
    try:
        for record in event["Records"]:
            message = json.loads(record["body"])
            msg = json.loads(message.get("Message", "{}"))
            event_type = msg.get("eventType")

            if event_type == "song_uploaded":
                process_song_uploaded(msg)
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
                "reason": f"Novo za tvoj {target_type.lower()}: {target_id}",
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
        "score": r * 2,
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

def process_user_unsubscribed(msg):
    user_id = msg.get("userId")
    target_id = msg.get("targetId")

    last_key = None
    while True:
        q = {
            "KeyConditionExpression": Key("userId").eq(user_id),
            "ScanIndexForward": False,
            "FilterExpression": Attr("contentId").eq(target_id) & Attr("type").eq("META"),
            "Limit": 100,
        }
        if last_key:
            q["ExclusiveStartKey"] = last_key

        resp = feed_table.query(**q)
        for it in resp.get("Items", []):
            feed_table.delete_item(Key={"userId": user_id, "createdAt": it["createdAt"]})
        if not resp.get("LastEvaluatedKey"):
            break
