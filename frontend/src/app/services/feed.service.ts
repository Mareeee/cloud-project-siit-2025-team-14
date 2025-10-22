import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../env/environment';
import { FeedItem } from '../models/feed.model';

@Injectable({ providedIn: 'root' })
export class FeedService {
    private stagePath = '/dev';
    private url = environment.apiBaseUrl + this.stagePath;

    constructor(private http: HttpClient) { }

    getFeed(): Observable<FeedItem[]> {
        return this.http.get<{ items: FeedItem[] }>(`${this.url}/feed`).pipe(
            map(res => res?.items ?? [])
        );
    }
}
