from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb
)

class SeederStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.seeder_lambda = _lambda.Function(
            self, "SeederLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="seeder.seed_data.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "GENRES_TABLE": "GenresTable",
                "ARTISTS_TABLE": "ArtistsTable",
                "ALBUMS_TABLE": "AlbumsTable",
                "SONGS_TABLE": "SongsTable",
                "RATINGS_TABLE": "RatingsTable",
                "SUBSCRIPTIONS_TABLE": "SubscriptionsTable",
            },
        )

        table_names = [
            "GenresTable",
            "ArtistsTable",
            "AlbumsTable",
            "SongsTable",
            "RatingsTable",
            "SubscriptionsTable",
        ]

        for name in table_names:
            try:
                table = dynamodb.Table.from_table_name(self, f"{name}Ref", name)
                table.grant_read_write_data(self.seeder_lambda)
            except Exception:
                print(f"Warning: Table {name} not found yet (will require existing tables).")
