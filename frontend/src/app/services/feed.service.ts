import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../env/environment';
import { SongFeedItem, AlbumFeedItem, ArtistFeedItem } from '../models/feed.model';

export type FeedBuckets = {
    songs: SongFeedItem[];
    artists: ArtistFeedItem[];
    albums: AlbumFeedItem[];
};

@Injectable({ providedIn: 'root' })
export class FeedService {
    private stagePath = '/dev';
    private url = environment.apiBaseUrl + this.stagePath;

    constructor(private http: HttpClient) { }

    getFeed(userId: string): Observable<FeedBuckets> {
        const params = new HttpParams().set('userId', userId);
        return this.http
            .get<{ feed: FeedBuckets }>(`${this.url}/feed`, { params })
            .pipe(
                map(res => {
                    const f = res?.feed ?? { songs: [], artists: [], albums: [] };
                    return {
                        songs: Array.isArray(f.songs) ? f.songs : [],
                        artists: Array.isArray(f.artists) ? f.artists : [],
                        albums: Array.isArray(f.albums) ? f.albums : [],
                    } as FeedBuckets;
                })
            );
    }

    listenSong(userId: string, songId: string): Observable<any> {
        return this.http.put<any>(`${this.url}/songs/listen/${songId}/${userId}`, {});
    }
}
