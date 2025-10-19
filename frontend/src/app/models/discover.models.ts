export interface GenreEntityBase {
    entityType: 'ARTIST' | 'ALBUM' | 'SONG';
    entityId: string;
    PK: string;
    SK: string;
}

export interface DiscoverArtist extends GenreEntityBase {
    entityType: 'ARTIST';
    name: string;
}

export interface DiscoverAlbum extends GenreEntityBase {
    entityType: 'ALBUM';
    title: string;
    releaseDate: string;
}

export interface DiscoverSong extends GenreEntityBase {
    entityType: 'SONG';
    title: string;
    creationDate: string;
    s3KeyCover?: string;
    s3KeyAudio?: string;
    genres?: string[];
    imageUrl?: string;
    audioUrl?: string;
    isPlaying?: boolean;
    currentTime?: number;
    duration?: number;
}
