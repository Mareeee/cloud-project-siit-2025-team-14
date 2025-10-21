from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_sns as sns,
    aws_iam as iam,
    aws_sns_subscriptions as subs,
    aws_ses as ses
)

class SubscriptionsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, artist_table, genre_table, topic, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.subscriptions_table = dynamodb.Table(
            self, "SubscriptionsTable",
            table_name="SubscriptionsTable",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="targetId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.subscriptions_table.add_global_secondary_index(
            index_name="targetId-index",
            partition_key=dynamodb.Attribute(name="targetId", type=dynamodb.AttributeType.STRING)
        )

        self.subscriptions_table.add_global_secondary_index(
            index_name="subscriptionId-index",
            partition_key=dynamodb.Attribute(name="subscriptionId", type=dynamodb.AttributeType.STRING)
        )

        self.verified_email = ses.EmailIdentity(
            self,
            "VerifiedSourceEmail",
            identity=ses.Identity.email("eventplannerteam18@gmail.com")
        )

        self.notifier_lambda = _lambda.Function(
            self, "NotifierFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="subscriptions.notifier.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": self.subscriptions_table.table_name,
                "SOURCE_EMAIL": self.verified_email.email_identity_name
            },
        )

        self.notifier_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["ses:SendEmail", "ses:SendRawEmail"],
            resources=["*"]
        ))

        topic.add_subscription(subs.LambdaSubscription(self.notifier_lambda))

        self.create_subscription_lambda = _lambda.Function(
            self, "CreateSubscriptionLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="subscriptions.create_subscription.handler",
            environment={
                "TABLE_NAME": self.subscriptions_table.table_name
            },
        )

        self.get_subscriptions_lambda = _lambda.Function(
            self, "GetSubscriptionsLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="subscriptions.get_subscriptions.handler",
            environment={
                "SUBSCRIPTIONS_TABLE": self.subscriptions_table.table_name,
                "ARTISTS_TABLE": artist_table.table_name,
                "GENRES_TABLE": genre_table.table_name
            },
        )
        artist_table.grant_read_data(self.get_subscriptions_lambda)
        genre_table.grant_read_data(self.get_subscriptions_lambda)

        self.delete_subscription_lambda = _lambda.Function(
            self, "DeleteSubscriptionLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="subscriptions.delete_subscription.handler",
            environment={
                "TABLE_NAME": self.subscriptions_table.table_name
            },
        )

        self.subscriptions_table.grant_read_data(self.notifier_lambda)
        self.subscriptions_table.grant_read_write_data(self.create_subscription_lambda)
        self.subscriptions_table.grant_read_write_data(self.get_subscriptions_lambda)
        self.subscriptions_table.grant_read_write_data(self.delete_subscription_lambda)