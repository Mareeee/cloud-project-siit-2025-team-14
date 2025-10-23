import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../env/environment';
import { FeedItem } from '../models/feed.model';

@Injectable({ providedIn: 'root' })
export class FeedService {
    private stagePath = '/dev';
    private url = environment.apiBaseUrl + this.stagePath;

    constructor(private http: HttpClient) { }

    getFeed(userId: string): Observable<FeedItem[]> {
        const params = new HttpParams().set('userId', userId);
        return this.http
            .get<{ feed: FeedItem[] }>(`${this.url}/feed`, { params })
            .pipe(map(res => res?.feed ?? []));
    }

    listenSong(userId: string, songId: string): Observable<any> {
        return this.http.post<any>(`${this.url}/songs/listen/${songId}/${userId}`, {});
    }
}
