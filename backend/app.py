#!/usr/bin/env python3
import aws_cdk as cdk

from backend_stack.genres_stack import GenresStack
from backend_stack.artists_stack import ArtistsStack
from backend_stack.albums_stack import AlbumsStack
from backend_stack.songs_stack import SongsStack
from backend_stack.api_stack import ApiStack

app = cdk.App()

genres_stack = GenresStack(app, "GenresStack")

artists_stack = ArtistsStack(app, "ArtistsStack", genres_table=genres_stack.genres_table)
albums_stack = AlbumsStack(app, "AlbumsStack", genres_table=genres_stack.genres_table)
songs_stack = SongsStack(app, "SongsStack", genres_table=genres_stack.genres_table)

ApiStack(app, "ApiStack",
          songs_stack=songs_stack,
          artists_stack=artists_stack,
          albums_stack=albums_stack)

app.synth()
