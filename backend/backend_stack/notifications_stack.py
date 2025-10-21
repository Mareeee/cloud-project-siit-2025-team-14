from aws_cdk import (
    Stack,
    aws_sns as sns
)
from constructs import Construct

class NotificationsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.topic = sns.Topic(
            self, "NewContentTopic",
            topic_name="NewContentTopic"
        )
