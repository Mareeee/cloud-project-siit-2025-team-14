from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_s3 as s3
)

class GenreCatalogStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.genre_catalog_table = dynamodb.Table(
            self, "GenreCatalogTable",
            table_name="GenreCatalogTable",
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        self.genre_catalog_table.add_global_secondary_index(
            index_name="EntityTypeIndex",
            partition_key=dynamodb.Attribute(name="entityType", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING)
        )

        self.genre_catalog_table.add_global_secondary_index(
            index_name="BySongIndex",
            partition_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )

        self.get_entities_by_genre_lambda = _lambda.Function(
            self, "GetEntitiesByGenreLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="genre_catalog.get_entities_by_genre.handler",
            environment={
                "GENRE_CATALOG_TABLE": self.genre_catalog_table.table_name,
                "MEDIA_BUCKET_NAME": "songs-media",
            }
        )

        media_bucket = s3.Bucket.from_bucket_name(self, "SongsMediaImported", "songs-media")
        
        media_bucket.grant_read(self.get_entities_by_genre_lambda)
        self.genre_catalog_table.grant_read_data(self.get_entities_by_genre_lambda)
