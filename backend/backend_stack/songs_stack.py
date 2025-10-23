from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_events
)

class SongsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, genres_table, genre_catalog_table, ratings_table, notifications_topic, feed_topic, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.songs_table = dynamodb.Table(
            self, "SongsTable",
            table_name="SongsTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="title", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.songs_table.add_global_secondary_index(
            index_name="AlbumIndex",
            partition_key=dynamodb.Attribute(
                name="albumId",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        self.songs_table.add_global_secondary_index(
            index_name="SongIdIndex",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING)
        )

        self.artist_catalog_table = dynamodb.Table(
            self, "ArtistCatalogTable",
            table_name="ArtistCatalogTable",
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.artist_catalog_table.add_global_secondary_index(
            index_name="BySongIndex",
            partition_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )

        self.transcribe_queue = sqs.Queue(
            self, "TranscriptionQueue",
            visibility_timeout=Duration.seconds(660)
        )

        self.media_bucket = s3.Bucket(
            self, "MediaBucket",
            bucket_name="songs-media",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.PUT, s3.HttpMethods.GET],
                allowed_origins=["*"],
                allowed_headers=["*"]
            )]
        )

        self.transcription_worker = _lambda.DockerImageFunction(
            self, "TranscriptionWorker",
            code=_lambda.DockerImageCode.from_image_asset(
                "lambda/transcriptions/whisper_worker"
            ),
            timeout=Duration.minutes(5),
            memory_size=2048,
            environment={
                "TRANSCRIPTIONS_BUCKET": self.media_bucket.bucket_name
            }
        )

        self.transcribe_queue.grant_consume_messages(self.transcription_worker)

        _lambda.EventSourceMapping(
            self, "TranscriptionQueueMapping",
            target=self.transcription_worker,
            event_source_arn=self.transcribe_queue.queue_arn,
            batch_size=5,
        )

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
            handler="transcriptions.transcription_result.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.minutes(1),
            environment={
                "TRANSCRIPTIONS_TABLE": self.transcriptions_table.table_name,
            }
        )

        self.transcriptions_table.grant_write_data(self.transcription_result_handler)

        self.media_bucket.grant_read_write(self.transcription_worker)
        self.media_bucket.grant_read(self.transcription_result_handler)
        self.transcription_result_handler.add_event_source(
            lambda_events.S3EventSource(
                self.media_bucket,
                events=[s3.EventType.OBJECT_CREATED],
                filters=[s3.NotificationKeyFilter(prefix="lyrics/")]
            )
        )

        self.get_songs_lambda = _lambda.Function(
            self, 'GetSongsLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='songs.get_songs.handler',
            environment={
                "SONGS_TABLE": self.songs_table.table_name,
                "MEDIA_BUCKET": self.media_bucket.bucket_name,
                "GENRES_TABLE": genres_table.table_name
            }
        )

        self.listen_song_lambda = _lambda.Function(
            self, 'ListenSongLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='songs.listen_song.handler',
            environment={
                "SONGS_TABLE": self.songs_table.table_name,
                "FEED_TOPIC_ARN": feed_topic.topic_arn,
            }
        )

        feed_topic.grant_publish(self.listen_song_lambda)

        self.create_song_lambda = _lambda.Function(
            self, 'CreateSongLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='songs.create_song.handler',
            environment={
                "SONGS_TABLE": self.songs_table.table_name,
                "MEDIA_BUCKET": self.media_bucket.bucket_name,
                "GENRES_TABLE": genres_table.table_name,
                "GENRE_CATALOG_TABLE": genre_catalog_table.table_name,
                "ARTIST_CATALOG_TABLE": self.artist_catalog_table.table_name,
                "FEED_TOPIC_ARN": feed_topic.topic_arn,
                "NOTIFICATIONS_TOPIC_ARN": notifications_topic.topic_arn
            }
        )

        self.create_song_lambda.add_environment("TRANSCRIPTION_QUEUE_URL", self.transcribe_queue.queue_url)
        self.transcribe_queue.grant_send_messages(self.create_song_lambda)

        feed_topic.grant_publish(self.create_song_lambda)
        notifications_topic.grant_publish(self.create_song_lambda)

        self.edit_song_lambda = _lambda.Function(
            self, 'EditSongLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='songs.edit_song.handler',
            environment={
                "SONGS_TABLE": self.songs_table.table_name,
                "MEDIA_BUCKET": self.media_bucket.bucket_name,
                "GENRES_TABLE": genres_table.table_name,
                "GENRE_CATALOG_TABLE": genre_catalog_table.table_name,
                "ARTIST_CATALOG_TABLE": self.artist_catalog_table.table_name
            }
        )

        self.delete_song_lambda = _lambda.Function(
            self, 'DeleteSongLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='songs.delete_song.handler',
            environment={
                "SONGS_TABLE": self.songs_table.table_name,
                "MEDIA_BUCKET": self.media_bucket.bucket_name,
                "GENRES_TABLE": genres_table.table_name,
                "GENRE_CATALOG_TABLE": genre_catalog_table.table_name,
                "ARTIST_CATALOG_TABLE": self.artist_catalog_table.table_name,
                "RATINGS_TABLE": ratings_table.table_name
            }
        )

        self.get_songs_by_artist_lambda = _lambda.Function(
            self, 'GetSongsByArtistLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='songs.get_songs_by_artist.handler',
            environment={
                "SONGS_TABLE": self.songs_table.table_name,
                "MEDIA_BUCKET": self.media_bucket.bucket_name,
                "ARTIST_CATALOG_TABLE": self.artist_catalog_table.table_name
            }
        )

        self.get_songs_by_album_lambda = _lambda.Function(
            self, 'GetSongsByAlbumLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='songs.get_songs_by_album.handler',
            environment={
                "SONGS_TABLE": self.songs_table.table_name,
                "MEDIA_BUCKET": self.media_bucket.bucket_name
            }
        )

        self.presign_lambda = _lambda.Function(
            self, "PresignLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="presign.generate_presign_url.handler",
            environment={
                "MEDIA_BUCKET": self.media_bucket.bucket_name
            }
        )
        
        self.download_song_lambda = _lambda.Function(
            self, "DownloadSongLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="songs.get_presigned_download_url.handler",
            environment={
                "SONGS_TABLE": self.songs_table.table_name,
                "MEDIA_BUCKET": self.media_bucket.bucket_name
            }
        )

        self.songs_table.grant_read_write_data(self.create_song_lambda)
        self.songs_table.grant_read_write_data(self.listen_song_lambda)
        self.songs_table.grant_read_write_data(self.get_songs_lambda)
        self.songs_table.grant_read_data(self.get_songs_by_artist_lambda)
        self.songs_table.grant_read_data(self.get_songs_by_album_lambda)
        self.songs_table.grant_read_write_data(self.delete_song_lambda)
        self.songs_table.grant_read_write_data(self.edit_song_lambda)
        self.songs_table.grant_read_data(self.download_song_lambda)
        self.media_bucket.grant_read(self.download_song_lambda)
        self.media_bucket.grant_read_write(self.create_song_lambda)
        self.media_bucket.grant_read_write(self.get_songs_lambda)
        self.media_bucket.grant_read_write(self.get_songs_by_artist_lambda)
        self.media_bucket.grant_read_write(self.get_songs_by_album_lambda)
        self.media_bucket.grant_read_write(self.delete_song_lambda)
        self.media_bucket.grant_read_write(self.edit_song_lambda)
        self.media_bucket.grant_put(self.presign_lambda)
        genres_table.grant_read_write_data(self.create_song_lambda)
        genres_table.grant_read_data(self.get_songs_lambda)
        genres_table.grant_read_data(self.edit_song_lambda)
        genre_catalog_table.grant_read_write_data(self.create_song_lambda)
        genre_catalog_table.grant_read_write_data(self.delete_song_lambda)
        genre_catalog_table.grant_read_write_data(self.edit_song_lambda)
        self.artist_catalog_table.grant_read_write_data(self.create_song_lambda)
        self.artist_catalog_table.grant_read_data(self.get_songs_by_artist_lambda)
        self.artist_catalog_table.grant_read_write_data(self.delete_song_lambda)
        self.artist_catalog_table.grant_read_write_data(self.edit_song_lambda)
        ratings_table.grant_read_write_data(self.delete_song_lambda)

        self.get_lyrics_lambda = _lambda.Function(
            self, "GetLyricsLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="transcriptions.get_lyrics.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TRANSCRIPTIONS_TABLE": self.transcriptions_table.table_name
            },
        )

        self.transcriptions_table.grant_read_data(self.get_lyrics_lambda)
