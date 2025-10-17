from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
)

class SubscriptionsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.subscriptions_table = dynamodb.Table(
            self, "SubscriptionsTable",
            table_name="SubscriptionsTable",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="targetId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.create_subscription_lambda = _lambda.Function(
            self, "CreateSubscriptionLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="subscriptions.create_subscription.handler",
            environment={"SUBSCRIPTIONS_TABLE": self.subscriptions_table.table_name}
        )

        self.get_subscriptions_lambda = _lambda.Function(
            self, "GetSubscriptionsLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="subscriptions.get_subscriptions.handler",
            environment={"SUBSCRIPTIONS_TABLE": self.subscriptions_table.table_name}
        )

        self.delete_subscription_lambda = _lambda.Function(
            self, "DeleteSubscriptionLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="subscriptions.delete_subscription.handler",
            environment={"SUBSCRIPTIONS_TABLE": self.subscriptions_table.table_name}
        )

        self.subscriptions_table.grant_read_write_data(self.create_subscription_lambda)
        self.subscriptions_table.grant_read_write_data(self.get_subscriptions_lambda)
        self.subscriptions_table.grant_read_write_data(self.delete_subscription_lambda)
