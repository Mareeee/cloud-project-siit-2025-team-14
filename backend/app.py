#!/usr/bin/env python3
import aws_cdk as cdk

from backend_stack.genres_stack import GenresStack
from backend_stack.artists_stack import ArtistsStack
from backend_stack.albums_stack import AlbumsStack
from backend_stack.songs_stack import SongsStack
from backend_stack.api_stack import ApiStack
from backend_stack.auth_stack import AuthStack
from backend_stack.notifications_stack import NotificationsStack
from backend_stack.ratings_stack import RatingsStack
from backend_stack.subscriptions_stack import SubscriptionsStack
from backend_stack.transcription_stack import TranscriptionStack
from backend_stack.seeder_stack import SeederStack

app = cdk.App()

genres_stack = GenresStack(app, "GenresStack")

artists_stack = ArtistsStack(app, "ArtistsStack", genres_table=genres_stack.genres_table)
albums_stack = AlbumsStack(app, "AlbumsStack", genres_table=genres_stack.genres_table, artists_table=artists_stack.artists_table)
songs_stack = SongsStack(app, "SongsStack", genres_table=genres_stack.genres_table)

auth_stack = AuthStack(app, "AuthStack")
notifications_stack = NotificationsStack(app, "NotificationsStack")
ratings_stack = RatingsStack(app, "RatingsStack")
subscriptions_stack = SubscriptionsStack(app, "SubscriptionsStack")
transcription_stack = TranscriptionStack(app, "TranscriptionStack")
seeder_stack = SeederStack(app, "SeederStack")

ApiStack(app, "ApiStack",
          songs_stack=songs_stack,
          artists_stack=artists_stack,
          albums_stack=albums_stack,
          ratings_stack=ratings_stack,
          subscriptions_stack=subscriptions_stack,
          notifications_stack=notifications_stack,
          transcription_stack=transcription_stack,
          genres_stack=genres_stack)

app.synth()
