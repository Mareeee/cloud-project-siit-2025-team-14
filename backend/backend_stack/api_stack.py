from constructs import Construct
from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_cognito as cognito,
)

class ApiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        songs_stack,
        artists_stack,
        albums_stack,
        ratings_stack,
        subscriptions_stack,
        transcription_stack,
        genres_stack,
        genre_catalog_stack,
        auth_stack,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        api = apigw.RestApi(
            self, "SongsApi",
            rest_api_name="SongsAPI",
            deploy=True,
            deploy_options=apigw.StageOptions(stage_name="dev"),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=["GET", "OPTIONS", "PUT", "POST", "DELETE"],
                allow_headers=["Content-Type", "Authorization"],
            )
        )

        user_pool = cognito.UserPool.from_user_pool_id(
            self, "ImportedUserPool",
            user_pool_id=auth_stack.user_pool.user_pool_id
        )

        authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "ApiAuthorizer",
            cognito_user_pools=[user_pool]
        )

        songs_res = api.root.add_resource("songs")
        songs_res.add_method("GET", apigw.LambdaIntegration(songs_stack.get_songs_lambda))
        songs_res.add_method("PUT", apigw.LambdaIntegration(songs_stack.create_song_lambda))
        songs_res.add_resource("{songId}").add_method("DELETE", apigw.LambdaIntegration(songs_stack.delete_song_lambda))
        songs_res.add_resource("edit").add_resource("{songId}").add_method("PUT", apigw.LambdaIntegration(songs_stack.edit_song_lambda))
        songs_res.add_resource("artist").add_resource("{artistId}").add_method(
            "GET", apigw.LambdaIntegration(songs_stack.get_songs_by_artist_lambda)
        )
        songs_res.add_resource("album").add_resource("{albumId}").add_method(
            "GET", apigw.LambdaIntegration(songs_stack.get_songs_by_album_lambda)
        )
        songs_download_res = songs_res.add_resource("download")
        songs_download_by_id_title = songs_download_res.add_resource("{songId}").add_resource("{title}")
        songs_download_by_id_title.add_method(
            "GET", apigw.LambdaIntegration(songs_stack.download_song_lambda)
        )

        genres_res = api.root.add_resource("genres")
        genres_res.add_method("GET", apigw.LambdaIntegration(genres_stack.get_genres_lambda))

        genre_catalog_res = api.root.add_resource("discover")
        genre_catalog_res.add_resource("{genre}").add_method(
            "GET",
            apigw.LambdaIntegration(genre_catalog_stack.get_entities_by_genre_lambda)
        )

        artists_res = api.root.add_resource("artists")
        artists_res.add_method("GET", apigw.LambdaIntegration(artists_stack.get_artists_lambda))
        artists_res.add_method(
            "POST", apigw.LambdaIntegration(artists_stack.create_artist_lambda),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=authorizer)

        albums_res = api.root.add_resource("albums")
        albums_res.add_method("GET", apigw.LambdaIntegration(albums_stack.get_albums_lambda))
        albums_res.add_method("POST", apigw.LambdaIntegration(albums_stack.create_album_lambda))

        presign_res = api.root.add_resource("presign")
        presign_res.add_method("GET", apigw.LambdaIntegration(songs_stack.presign_lambda))

        subs_res = api.root.add_resource("subscriptions")
        subs_res.add_method(
            "POST", apigw.LambdaIntegration(subscriptions_stack.create_subscription_lambda),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        subs_res.add_method(
            "GET", apigw.LambdaIntegration(subscriptions_stack.get_subscriptions_lambda),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        subs_res.add_method(
            "DELETE", apigw.LambdaIntegration(subscriptions_stack.delete_subscription_lambda),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        new_content_res = api.root.add_resource("new-content")
        new_content_res.add_method("POST", apigw.LambdaIntegration(subscriptions_stack.notifier_lambda))

        ratings_res = api.root.add_resource("ratings")
        ratings_res.add_method("POST", apigw.LambdaIntegration(ratings_stack.create_rating_lambda))
        ratings_res.add_method("GET", apigw.LambdaIntegration(ratings_stack.get_ratings_lambda))
        ratings_res.add_method("DELETE", apigw.LambdaIntegration(ratings_stack.delete_rating_lambda))

        transcribe_res = api.root.add_resource("transcribe")
        transcribe_res.add_method(
            "POST", apigw.LambdaIntegration(transcription_stack.transcription_worker)
        )
