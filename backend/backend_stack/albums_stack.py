from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb
)

class AlbumsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, genres_table, artists_table, genre_catalog_table, topic, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.albums_table = dynamodb.Table(
            self, "AlbumsTable",
            table_name="AlbumsTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="title", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.create_album_lambda = _lambda.Function(
            self, 'CreateAlbumLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='albums.create_album.handler',
            environment={
                "ALBUMS_TABLE": self.albums_table.table_name,
                "GENRES_TABLE": genres_table.table_name,
                "ARTISTS_TABLE": artists_table.table_name,
                "GENRE_CATALOG_TABLE": genre_catalog_table.table_name,
                "TOPIC_ARN": topic.topic_arn
            }
        )

        self.delete_album_lambda = _lambda.Function(
            self, 'DeleteAlbumLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='albums.delete_album.handler',
            environment={
                "ALBUMS_TABLE": self.albums_table.table_name,
                "GENRES_TABLE": genres_table.table_name,
                "ARTISTS_TABLE": artists_table.table_name,
                "GENRE_CATALOG_TABLE": genre_catalog_table.table_name
            }
        )
        
        topic.grant_publish(self.create_album_lambda)

        self.get_albums_lambda = _lambda.Function(
            self, 'GetAlbumsLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='albums.get_albums.handler',
            environment={
                "ALBUMS_TABLE": self.albums_table.table_name,
                "GENRES_TABLE": genres_table.table_name
            }
        )

        self.albums_table.grant_read_write_data(self.create_album_lambda)
        self.albums_table.grant_read_write_data(self.get_albums_lambda)

        genres_table.grant_read_write_data(self.create_album_lambda)
        genres_table.grant_read_data(self.get_albums_lambda)

        artists_table.grant_read_data(self.create_album_lambda)
        
        genre_catalog_table.grant_read_write_data(self.create_album_lambda)
