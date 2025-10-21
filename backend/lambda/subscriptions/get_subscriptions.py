import os
import boto3
from boto3.dynamodb.conditions import Key
from utils.utils import create_response

dynamodb = boto3.resource('dynamodb')

subscriptions_table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE'])
artists_table = dynamodb.Table(os.environ['ARTISTS_TABLE'])
genres_table = dynamodb.Table(os.environ['GENRES_TABLE'])

def handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        user_id = params.get("userId")

        if not user_id:
            return create_response(400, {"message": "User ID required."})

        response = subscriptions_table.query(KeyConditionExpression=Key("userId").eq(user_id))
        items = response.get("Items", [])

        result = []

        for sub in items:
            target_id = sub["targetId"]
            target_type = sub["targetType"]
            target_name = None

            if target_type.lower() == "artist":
                artist_resp = artists_table.query(
                    IndexName="ArtistIdIndex",
                    KeyConditionExpression=Key("id").eq(target_id),
                    Limit=1
                )
                artists = artist_resp.get("Items", [])
                if artists:
                    target_name = artists[0].get("name")

            elif target_type.lower() == "genre":
                genre_resp = genres_table.query(
                    IndexName="GenreIdIndex",
                    KeyConditionExpression=Key("id").eq(target_id),
                    Limit=1
                )
                genres = genre_resp.get("Items", [])
                if genres:
                    target_name = genres[0].get("name")

            if not target_name:
                target_name = f"Unknown {target_type}"

            result.append({
                "subscriptionId": sub.get("subscriptionId"),
                "targetName": target_name,
                "targetType": target_type,
                "createdAt": sub.get("createdAt")
            })

        return create_response(200, {"data": result})

    except Exception as e:
        print(f"Error in get_subscriptions: {e}")
        return create_response(500, {"message": str(e)})