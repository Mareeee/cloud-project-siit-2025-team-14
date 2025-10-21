from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda
)

class RatingsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.ratings_table = dynamodb.Table(
            self, "RatingsTable",
            table_name="RatingsTable",
            partition_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.ratings_table.add_global_secondary_index(
            index_name="BySongIndex",
            partition_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )

        self.create_rating_lambda = _lambda.Function(
            self, "CreateRatingLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="ratings.create_rating.handler",
            environment={"RATINGS_TABLE": self.ratings_table.table_name}
        )

        self.get_ratings_lambda = _lambda.Function(
            self, "GetRatingsLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="ratings.get_ratings.handler",
            environment={"RATINGS_TABLE": self.ratings_table.table_name}
        )

        self.delete_rating_lambda = _lambda.Function(
            self, "DeleteRatingLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="ratings.delete_rating.handler",
            environment={"RATINGS_TABLE": self.ratings_table.table_name}
        )

        self.ratings_table.grant_read_write_data(self.create_rating_lambda)
        self.ratings_table.grant_read_write_data(self.get_ratings_lambda)
        self.ratings_table.grant_read_write_data(self.delete_rating_lambda)
