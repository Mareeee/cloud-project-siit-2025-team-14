#!/usr/bin/env python3
import aws_cdk as cdk

from backend_stack.genres_stack import GenresStack
from backend_stack.artists_stack import ArtistsStack
from backend_stack.albums_stack import AlbumsStack
from backend_stack.songs_stack import SongsStack
from backend_stack.api_stack import ApiStack
from backend_stack.auth_stack import AuthStack
from backend_stack.ratings_stack import RatingsStack
from backend_stack.subscriptions_stack import SubscriptionsStack
from backend_stack.transcription_stack import TranscriptionStack
from backend_stack.seeder_stack import SeederStack
from backend_stack.genre_catalog_stack import GenreCatalogStack
from backend_stack.notifications_stack import NotificationsStack

app = cdk.App()

notifications_stack = NotificationsStack(app, "NotificationsStack")
genres_stack = GenresStack(app, "GenresStack")
genre_catalog_stack = GenreCatalogStack(app, "GenreCatalogStack")
auth_stack = AuthStack(app, "AuthStack")
ratings_stack = RatingsStack(app, "RatingsStack")
songs_stack = SongsStack(app, "SongsStack", genres_table=genres_stack.genres_table, genre_catalog_table=genre_catalog_stack.genre_catalog_table, ratings_table=ratings_stack.ratings_table, topic=notifications_stack.topic)
artists_stack = ArtistsStack(app, "ArtistsStack", genres_table=genres_stack.genres_table, genre_catalog_table=genre_catalog_stack.genre_catalog_table, artist_catalog_table=songs_stack.artist_catalog_table, topic=notifications_stack.topic)
subscriptions_stack = SubscriptionsStack(app, "SubscriptionsStack", artist_table=artists_stack.artists_table, genre_table=genres_stack.genres_table, topic=notifications_stack.topic)
albums_stack = AlbumsStack(app, "AlbumsStack", genres_table=genres_stack.genres_table, artists_table=artists_stack.artists_table, genre_catalog_table=genre_catalog_stack.genre_catalog_table, artists_stack_lambda=artists_stack.delete_artist_lambda, topic=notifications_stack.topic)
transcription_stack = TranscriptionStack(app, "TranscriptionStack")
seeder_stack = SeederStack(app, "SeederStack")

ApiStack(app, "ApiStack",
          songs_stack=songs_stack,
          artists_stack=artists_stack,
          albums_stack=albums_stack,
          ratings_stack=ratings_stack,
          subscriptions_stack=subscriptions_stack,
          transcription_stack=transcription_stack,
          genres_stack=genres_stack,
          genre_catalog_stack=genre_catalog_stack,
          auth_stack=auth_stack)

app.synth()
