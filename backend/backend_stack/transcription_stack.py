from constructs import Construct
from aws_cdk import (
    Stack,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_events,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    Duration,
    RemovalPolicy
)

class TranscriptionStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.transcribe_queue = sqs.Queue(
            self, "TranscriptionQueue",
            visibility_timeout=Duration.seconds(300)
        )

        self.transcription_worker = _lambda.Function(
            self, "TranscriptionWorker",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="transcription_worker.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.minutes(5)
        )

        self.transcribe_queue.grant_consume_messages(self.transcription_worker)

        self.transcriptions_table = dynamodb.Table(
            self, "TranscriptionsTable",
            partition_key=dynamodb.Attribute(
                name="song_id",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        self.transcription_result_handler = _lambda.Function(
            self, "TranscriptionResultHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="transcription_result.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.minutes(1),
            environment={
                "TRANSCRIPTIONS_TABLE": self.transcriptions_table.table_name,
            }
        )

        self.transcriptions_table.grant_write_data(self.transcription_result_handler)

        def attach_songs_bucket(self, bucket: s3.Bucket):
            bucket.grant_read_write(self.transcription_worker)
            bucket.grant_read(self.transcription_result_handler)
            self.transcription_result_handler.add_event_source(
                lambda_events.S3EventSource(
                    bucket,
                    events=[s3.EventType.OBJECT_CREATED],
                    filters=[s3.NotificationKeyFilter(prefix="lyrics/")]
                )
            )
