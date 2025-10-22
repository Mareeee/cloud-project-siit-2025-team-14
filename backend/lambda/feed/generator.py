import os
import json
import boto3
import time
from datetime import datetime
from boto3.dynamodb.conditions import Key

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

        return {"statusCode": 200}
    except Exception as e:
        print("Error:", e)
        return {"statusCode": 500, "body": str(e)}

def process_song_uploaded(msg):
    song_id = msg.get("songId")
    title = msg.get("title")
    artist_ids = msg.get("artistIds", [])
    genres = msg.get("genres", [])
    timestamp = msg.get("timestamp")

    all_target_ids = artist_ids + genres

    for target_id in all_target_ids:
        response = subscriptions_table.query(
            IndexName="targetId-index",
            KeyConditionExpression=Key("targetId").eq(target_id)
        )
        for item in response.get("Items", []):
            user_id = item["userId"]
            feed_table.put_item(Item={
                "userId": user_id,
                "createdAt": str(int(time.time())),
                "contentId": song_id,
                "title": title,
                "reason": f"New content for {target_id}",
                "timestamp": timestamp
            })

def process_user_rated(msg):
    user_id = msg.get("userId")
    content_id = msg.get("contentId")
    rating = msg.get("rating")

    feed_table.put_item(Item={
        "userId": user_id,
        "createdAt": str(int(time.time())),
        "contentId": content_id,
        "reason": f"You rated a song {rating}",
        "timestamp": datetime.utcnow().isoformat()
    })

def process_user_subscribed(msg):
    user_id = msg.get("userId")
    target_id = msg.get("targetId")
    target_type = msg.get("targetType")

    feed_table.put_item(Item={
        "userId": user_id,
        "createdAt": str(int(time.time())),
        "contentId": target_id,
        "reason": f"Subscribed to {target_type} {target_id}",
        "timestamp": datetime.utcnow().isoformat()
    })

def process_user_unsubscribed(msg):
    user_id = msg.get("userId")
    target_id = msg.get("targetId")

    feed_table.put_item(Item={
        "userId": user_id,
        "createdAt": str(int(time.time())),
        "contentId": target_id,
        "reason": f"Unsubscribed from {target_id}",
        "timestamp": datetime.utcnow().isoformat()
    })
