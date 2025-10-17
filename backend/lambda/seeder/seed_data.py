import boto3
import uuid
import json
from decimal import Decimal
from seeder.utils.utils import create_response

dynamodb = boto3.resource("dynamodb")

TABLES = [
    "GenresTable",
    "ArtistsTable",
    "AlbumsTable",
    "SongsTable",
    "RatingsTable",
    "SubscriptionsTable",
]

def clear_tables():
    table_keys = {
        "GenresTable": ("id", "name"),
        "ArtistsTable": ("id", "name"),
        "AlbumsTable": ("id", "title"),
        "SongsTable": ("id", "title"),
        "RatingsTable": ("contentId", "userId"),
        "SubscriptionsTable": ("userId", "targetId"),
    }

    for table_name, keys in table_keys.items():
        table = dynamodb.Table(table_name)
        print(f"Clearing table: {table_name}")
        scan = table.scan()
        with table.batch_writer() as batch:
            for item in scan.get("Items", []):
                key = {k: item[k] for k in keys if k in item}
                if len(key) == len(keys):
                    batch.delete_item(Key=key)
        print(f"Cleared {table_name}")


def handler(event, context):
    try:
        if event.get("reset", True):
            clear_tables()

        genres_table = dynamodb.Table("GenresTable")
        artists_table = dynamodb.Table("ArtistsTable")
        albums_table = dynamodb.Table("AlbumsTable")
        songs_table = dynamodb.Table("SongsTable")
        ratings_table = dynamodb.Table("RatingsTable")
        subscriptions_table = dynamodb.Table("SubscriptionsTable")

        genres = [
            {"id": str(uuid.uuid4()), "name": "Rock"},
            {"id": str(uuid.uuid4()), "name": "Pop"},
            {"id": str(uuid.uuid4()), "name": "Jazz"},
            {"id": str(uuid.uuid4()), "name": "Hip-Hop"},
            {"id": str(uuid.uuid4()), "name": "Classical"},
        ]
        for g in genres:
            genres_table.put_item(Item=g)

        genre_map = {g["name"]: g["id"] for g in genres}

        artists = [
            {"id": str(uuid.uuid4()), "name": "Queen", "genreIds": [genre_map["Rock"]]},
            {"id": str(uuid.uuid4()), "name": "Adele", "genreIds": [genre_map["Pop"], genre_map["Jazz"]]},
            {"id": str(uuid.uuid4()), "name": "Eminem", "genreIds": [genre_map["Hip-Hop"]]},
            {"id": str(uuid.uuid4()), "name": "Ludovico Einaudi", "genreIds": [genre_map["Classical"], genre_map["Jazz"]]},
        ]
        for a in artists:
            artists_table.put_item(Item=a)

        artist_map = {a["name"]: a["id"] for a in artists}

        albums = [
            {"id": str(uuid.uuid4()), "title": "Greatest Hits", "artistIds": [artist_map["Queen"]], "genreIds": [genre_map["Rock"]]},
            {"id": str(uuid.uuid4()), "title": "25", "artistIds": [artist_map["Adele"]], "genreIds": [genre_map["Pop"]]},
            {"id": str(uuid.uuid4()), "title": "Recovery", "artistIds": [artist_map["Eminem"]], "genreIds": [genre_map["Hip-Hop"], genre_map["Pop"]]},
            {"id": str(uuid.uuid4()), "title": "Elements", "artistIds": [artist_map["Ludovico Einaudi"]], "genreIds": [genre_map["Classical"], genre_map["Jazz"]]},
        ]
        for alb in albums:
            albums_table.put_item(Item=alb)

        album_map = {a["title"]: a["id"] for a in albums}

        songs = [
            {
                "id": str(uuid.uuid4()),
                "title": "Bohemian Rhapsody",
                "artistIds": [artist_map["Queen"]],
                "genreIds": [genre_map["Rock"]],
                "genres": ["Rock"],
                "album_id": album_map["Greatest Hits"],
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Hello",
                "artistIds": [artist_map["Adele"]],
                "genreIds": [genre_map["Pop"], genre_map["Jazz"]],
                "genres": ["Pop", "Jazz"],
                "album_id": album_map["25"],
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Not Afraid",
                "artistIds": [artist_map["Eminem"]],
                "genreIds": [genre_map["Hip-Hop"]],
                "genres": ["Hip-Hop"],
                "album_id": album_map["Recovery"],
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Nuvole Bianche",
                "artistIds": [artist_map["Ludovico Einaudi"]],
                "genreIds": [genre_map["Classical"], genre_map["Jazz"]],
                "genres": ["Classical", "Jazz"],
                "album_id": album_map["Elements"],
            },
        ]
        for s in songs:
            songs_table.put_item(Item=s)

        users = ["user1", "user2", "user3"]
        for s in songs:
            for u in users:
                rating_value = Decimal(3 + (hash(u + s["title"]) % 3))
                ratings_table.put_item(Item={
                    "contentId": s["id"],
                    "userId": u,
                    "rating": rating_value
                })

        subscriptions = [
            {"userId": "user1", "targetId": artist_map["Queen"], "targetType": "artist"},
            {"userId": "user2", "targetId": genre_map["Jazz"], "targetType": "genre"},
            {"userId": "user3", "targetId": album_map["25"], "targetType": "album"},
        ]
        for sub in subscriptions:
            subscriptions_table.put_item(Item=sub)

        return create_response(200, {
            "message": "Seeding completed successfully!",
            "genres": len(genres),
            "artists": len(artists),
            "albums": len(albums),
            "songs": len(songs),
            "ratings": len(songs) * len(users),
            "subscriptions": len(subscriptions)
        })

    except Exception as e:
        return create_response(500, {"message": str(e)})
