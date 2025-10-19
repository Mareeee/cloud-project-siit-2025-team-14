import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Genre } from '../models/genre.model';
import { environment } from '../../env/environment';

@Injectable({
    providedIn: 'root'
})
export class GenresService {
    private stagePath = '/dev';
    private resourcePath = '/genres';
    private url = environment.apiBaseUrl + this.stagePath + this.resourcePath;

    constructor(private http: HttpClient) { }

    getGenres(): Observable<{ data: Genre[] }> {
        return this.http.get<{ data: Genre[] }>(this.url);
    }

    getEntitiesByGenre(genre: string): Observable<{ data: any[] }> {
        const discoverUrl = `${environment.apiBaseUrl}${this.stagePath}/discover/${encodeURIComponent(genre)}`;
        return this.http.get<{ data: any[] }>(discoverUrl);
    }
}