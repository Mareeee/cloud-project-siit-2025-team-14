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
            self, "GenreSeederLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="seeder.seed_genres.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "GENRES_TABLE": "GenresTable",
            },
        )

        try:
            genres_table = dynamodb.Table.from_table_name(self, "GenresTableRef", "GenresTable")
            genres_table.grant_read_write_data(self.seeder_lambda)
        except Exception:
            print("Warning: GenresTable not found yet (will require existing table).")