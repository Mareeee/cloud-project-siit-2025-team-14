from constructs import Construct
from aws_cdk import (
    Stack,
    aws_sns as sns,
    aws_lambda as _lambda,
)

class NotificationsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.new_content_topic = sns.Topic(
            self, "NewContentTopic",
            topic_name="NewContentTopic"
        )

        self.publish_notification_lambda = _lambda.Function(
            self, "PublishNotificationLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="notifications.publish_notification.handler",
            environment={"TOPIC_ARN": self.new_content_topic.topic_arn}
        )
        self.new_content_topic.grant_publish(self.publish_notification_lambda)
