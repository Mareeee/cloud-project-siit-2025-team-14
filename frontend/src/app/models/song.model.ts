export interface Song {
    id: string;
    title: string;
    artistIds: string[];
    albumId: string;
    creationDate: string;
    genres: string[];
    imageUrl?: string;
    artistName?: string;
    artistBio?: string;
    audioUrl: string;
    artistNames?: string[];
    artistBios?: string[];
    artistGenres?: string[];
    isPlaying?: boolean;
    duration?: number;
    currentTime?: number;
}