from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb
)

class GenresStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.genres_table = dynamodb.Table(
            self, "GenresTable",
            table_name="GenresTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="name", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.get_genres_lambda = _lambda.Function(
            self, 'GetGenresLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='genres.get_genres.handler',
            environment={
                "GENRES_TABLE": self.genres_table.table_name
            }
        )

        self.genres_table.add_global_secondary_index(
            index_name="GenreNameIndex",
            partition_key=dynamodb.Attribute(name="name", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        self.genres_table.grant_read_data(self.get_genres_lambda)
