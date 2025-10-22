import { Album } from "./album.model";
import { Artist } from "./artist.model";
import { Song } from "./song.model";

export type FeedItemType = 'SONG' | 'ALBUM' | 'ARTIST';

export interface BaseFeedItem {
    type: FeedItemType;
    reason?: string;
}

export interface SongFeedItem extends BaseFeedItem {
    type: 'SONG';
    song: Song;
}

export interface AlbumFeedItem extends BaseFeedItem {
    type: 'ALBUM';
    album: Album;
}

export interface ArtistFeedItem extends BaseFeedItem {
    type: 'ARTIST';
    artist: Artist;
}

export type FeedItem = SongFeedItem | AlbumFeedItem | ArtistFeedItem;
