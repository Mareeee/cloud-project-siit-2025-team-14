from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_s3 as s3
)

class SongsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, genres_table, genre_catalog_table, **kwargs):
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
                "ARTIST_CATALOG_TABLE": self.artist_catalog_table.table_name
            }
        )

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
                "ARTIST_CATALOG_TABLE": self.artist_catalog_table.table_name
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
