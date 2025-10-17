from constructs import Construct
from aws_cdk import (
    Stack,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    Duration
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
            timeout=Duration.minutes(5),
            environment={
                "QUEUE_URL": self.transcribe_queue.queue_url
            }
        )

        self.transcribe_queue.grant_consume_messages(self.transcription_worker)
