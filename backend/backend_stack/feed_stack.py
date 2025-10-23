from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    aws_dynamodb as dynamodb,
    aws_sns_subscriptions as subs,
    aws_lambda_event_sources as events,
    aws_s3 as s3
)

class FeedStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, topic, songs_table, ratings_table, subscriptions_table, genres_table, albums_table, artists_table, genre_catalog_table, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.feed_queue = sqs.Queue(
            self, "FeedUpdateQueue",
            queue_name="FeedUpdateQueue",
            visibility_timeout=Duration.seconds(60),
            retention_period=Duration.days(4),
            removal_policy=RemovalPolicy.DESTROY
        )

        topic.add_subscription(subs.SqsSubscription(self.feed_queue))

        self.feed_table = dynamodb.Table(
            self, "UserFeedTable",
            table_name="UserFeedTable",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="createdAt", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.feed_generator_lambda = _lambda.Function(
            self, "FeedGeneratorLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="feed.generator.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "FEED_TABLE": self.feed_table.table_name,
                "SONGS_TABLE": songs_table.table_name,
                "RATINGS_TABLE": ratings_table.table_name,
                "SUBSCRIPTIONS_TABLE": subscriptions_table.table_name,
                "GENRES_TABLE": genres_table.table_name,
                "GENRE_CATALOG_TABLE": genre_catalog_table.table_name
            },
            timeout=Duration.seconds(30)
        )

        self.feed_generator_lambda.add_event_source(
            events.SqsEventSource(self.feed_queue, batch_size=5)
        )

        self.get_feed_lambda = _lambda.Function(
            self, "GetFeedLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="feed.get_feed.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "FEED_TABLE": self.feed_table.table_name,
                "SONGS_TABLE": songs_table.table_name,
                "ALBUMS_TABLE": albums_table.table_name,
                "ARTISTS_TABLE": artists_table.table_name,
                "MEDIA_BUCKET": "songs-media",
            },
            timeout=Duration.seconds(15)
        )

        self.feed_table.grant_read_write_data(self.feed_generator_lambda)
        self.feed_table.grant_read_data(self.get_feed_lambda)
        songs_table.grant_read_data(self.feed_generator_lambda)
        ratings_table.grant_read_data(self.feed_generator_lambda)
        subscriptions_table.grant_read_data(self.feed_generator_lambda)
        genres_table.grant_read_data(self.feed_generator_lambda)
        genre_catalog_table.grant_read_data(self.feed_generator_lambda)
        songs_table.grant_read_data(self.get_feed_lambda)
        albums_table.grant_read_data(self.get_feed_lambda)
        artists_table.grant_read_data(self.get_feed_lambda)
        
        media_bucket = s3.Bucket.from_bucket_name(self, "SongsMediaImported", "songs-media")
        media_bucket.grant_read(self.get_feed_lambda)
