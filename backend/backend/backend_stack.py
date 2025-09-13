from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
)

class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        songs_table = dynamodb.Table(
            self, "SongsTable",
            table_name="SongsTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="title", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        artists_table = dynamodb.Table(
            self, "ArtistsTable",
            table_name="ArtistsTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="name", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        media_bucket = s3.Bucket(
            self, "MediaBucket",
            bucket_name="songs-media",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.PUT, s3.HttpMethods.GET],
                allowed_origins=["*"],
                allowed_headers=["*"]
            )]
        )

        get_songs_lambda = _lambda.Function(
            self, 'GetSongsLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='songs.get_songs.handler',
            environment={
                "SONGS_TABLE": songs_table.table_name,
                "MEDIA_BUCKET": media_bucket.bucket_name
            }
        )

        create_song_lambda = _lambda.Function(
            self, 'CreateSongLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='songs.create_song.handler',
            environment={
                "SONGS_TABLE": songs_table.table_name,
                "MEDIA_BUCKET": media_bucket.bucket_name
            }        
        )

        create_artist_lambda = _lambda.Function(
            self, 'CreateArtistLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='artists.create_artist.handler',
            environment={
                "ARTISTS_TABLE": artists_table.table_name
            }
        )

        get_artists_lambda = _lambda.Function(
            self, 'GetArtistsLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='artists.get_artists.handler',
            environment={
                "ARTISTS_TABLE": artists_table.table_name
            }
        )

        songs_table.grant_read_write_data(get_songs_lambda)
        songs_table.grant_read_write_data(create_song_lambda)
        artists_table.grant_read_write_data(create_artist_lambda)
        artists_table.grant_read_write_data(get_artists_lambda)

        media_bucket.grant_read_write(get_songs_lambda)
        media_bucket.grant_read_write(create_song_lambda)

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

        songs_resource = api.root.add_resource("songs")
        songs_resource.add_method("GET", apigw.LambdaIntegration(get_songs_lambda))
        songs_resource.add_method("PUT", apigw.LambdaIntegration(create_song_lambda))

        artists_resource = api.root.add_resource("artists")
        artists_resource.add_method("GET", apigw.LambdaIntegration(get_artists_lambda))
        artists_resource.add_method("POST", apigw.LambdaIntegration(create_artist_lambda))
