from constructs import Construct
from aws_cdk import (
    Stack,
    aws_apigateway as apigw
)

class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, songs_stack, artists_stack, albums_stack, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        api = apigw.RestApi(
            self, "SongsApi",
            rest_api_name="SongsAPI",
            deploy=True,
            deploy_options=apigw.StageOptions(stage_name="dev"),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=["GET", "OPTIONS", "PUT", "POST"],
                allow_headers=["Content-Type", "Authorization"],
            )
        )

        songs_res = api.root.add_resource("songs")
        songs_res.add_method("GET", apigw.LambdaIntegration(songs_stack.get_songs_lambda))
        songs_res.add_method("PUT", apigw.LambdaIntegration(songs_stack.create_song_lambda))
        songs_res.add_resource("genre").add_resource("{genre}").add_method(
            "GET", apigw.LambdaIntegration(songs_stack.get_songs_by_genre_lambda)
        )
        songs_res.add_resource("artist").add_resource("{artistId}").add_method(
            "GET", apigw.LambdaIntegration(songs_stack.get_songs_by_artist_lambda)
        )
        songs_res.add_resource("album").add_resource("{albumId}").add_method(
            "GET", apigw.LambdaIntegration(songs_stack.get_songs_by_album_lambda)
        )

        artists_res = api.root.add_resource("artists")
        artists_res.add_method("GET", apigw.LambdaIntegration(artists_stack.get_artists_lambda))
        artists_res.add_method("POST", apigw.LambdaIntegration(artists_stack.create_artist_lambda))
        artists_res.add_resource("genre").add_resource("{genre}").add_method(
            "GET", apigw.LambdaIntegration(artists_stack.get_artists_by_genre_lambda)
        )

        albums_res = api.root.add_resource("albums")
        albums_res.add_method("GET", apigw.LambdaIntegration(albums_stack.get_albums_lambda))
        albums_res.add_method("POST", apigw.LambdaIntegration(albums_stack.create_album_lambda))
        albums_res.add_resource("genre").add_resource("{genre}").add_method(
            "GET", apigw.LambdaIntegration(albums_stack.get_albums_by_genre_lambda)
        )
