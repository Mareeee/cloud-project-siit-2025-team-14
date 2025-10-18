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
        notifications_stack,
        transcription_stack,
        genres_stack,
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
        songs_res.add_resource("genre").add_resource("{genre}").add_method(
            "GET", apigw.LambdaIntegration(songs_stack.get_songs_by_genre_lambda)
        )
        songs_res.add_resource("artist").add_resource("{artistId}").add_method(
            "GET", apigw.LambdaIntegration(songs_stack.get_songs_by_artist_lambda)
        )
        songs_res.add_resource("album").add_resource("{albumId}").add_method(
            "GET", apigw.LambdaIntegration(songs_stack.get_songs_by_album_lambda)
        )

        genres_res = api.root.add_resource("genres")
        genres_res.add_method("GET", apigw.LambdaIntegration(genres_stack.get_genres_lambda))

        artists_res = api.root.add_resource("artists")
        artists_res.add_method("GET", apigw.LambdaIntegration(artists_stack.get_artists_lambda))
        artists_res.add_method(
            "POST", apigw.LambdaIntegration(artists_stack.create_artist_lambda),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=authorizer)
        artists_res.add_resource("genre").add_resource("{genre}").add_method(
            "GET", apigw.LambdaIntegration(artists_stack.get_artists_by_genre_lambda)
        )

        albums_res = api.root.add_resource("albums")
        albums_res.add_method("GET", apigw.LambdaIntegration(albums_stack.get_albums_lambda))
        albums_res.add_method("POST", apigw.LambdaIntegration(albums_stack.create_album_lambda))
        albums_res.add_resource("genre").add_resource("{genre}").add_method(
            "GET", apigw.LambdaIntegration(albums_stack.get_albums_by_genre_lambda)
        )

        presign_res = api.root.add_resource("presign")
        presign_res.add_method("GET", apigw.LambdaIntegration(songs_stack.presign_lambda))

        subs_res = api.root.add_resource("subscriptions")
        subs_res.add_method(
            "POST", apigw.LambdaIntegration(subscriptions_stack.create_subscription_lambda)
        )
        subs_res.add_method(
            "GET", apigw.LambdaIntegration(subscriptions_stack.get_subscriptions_lambda)
        )
        subs_res.add_resource("{targetId}").add_method(
            "DELETE", apigw.LambdaIntegration(subscriptions_stack.delete_subscription_lambda)
        )

        ratings_res = api.root.add_resource("ratings")
        ratings_res.add_method("POST", apigw.LambdaIntegration(ratings_stack.create_rating_lambda))
        ratings_res.add_method("GET", apigw.LambdaIntegration(ratings_stack.get_ratings_lambda))

        notifications_res = api.root.add_resource("notifications")
        notifications_res.add_method(
            "POST", apigw.LambdaIntegration(notifications_stack.publish_notification_lambda)
        )

        transcribe_res = api.root.add_resource("transcribe")
        transcribe_res.add_method(
            "POST", apigw.LambdaIntegration(transcription_stack.transcription_worker)
        )
