from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb
)

class ArtistsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, genres_table, genre_catalog_table, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.artists_table = dynamodb.Table(
            self, "ArtistsTable",
            table_name="ArtistsTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="name", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        self.artists_table.add_global_secondary_index(
            index_name="ArtistIdIndex",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        self.create_artist_lambda = _lambda.Function(
            self, 'CreateArtistLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='artists.create_artist.handler',
            environment={
                "ARTISTS_TABLE": self.artists_table.table_name,
                "GENRES_TABLE": genres_table.table_name,
                "GENRE_CATALOG_TABLE": genre_catalog_table.table_name
            }
        )

        self.delete_artist_lambda = _lambda.Function(
            self, 'DeleteArtistLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='artists.delete_artist.handler',
            environment={
                "ARTISTS_TABLE": self.artists_table.table_name,
                "GENRES_TABLE": genres_table.table_name,
                "GENRE_CATALOG_TABLE": genre_catalog_table.table_name
            }
        )

        self.get_artists_lambda = _lambda.Function(
            self, 'GetArtistsLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='artists.get_artists.handler',
            environment={
                "ARTISTS_TABLE": self.artists_table.table_name,
                "GENRES_TABLE": genres_table.table_name
            }
        )

        self.artists_table.grant_read_write_data(self.create_artist_lambda)
        self.artists_table.grant_read_write_data(self.get_artists_lambda)
        genres_table.grant_read_data(self.create_artist_lambda)
        genres_table.grant_read_data(self.get_artists_lambda)

        genre_catalog_table.grant_read_write_data(self.create_artist_lambda)
