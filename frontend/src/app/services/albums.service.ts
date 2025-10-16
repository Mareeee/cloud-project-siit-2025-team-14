import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class AlbumsService {
    private apiUrl = 'https://35500nafx8.execute-api.eu-central-1.amazonaws.com';
    private stagePath = '/dev';
    private resourcePath = '/albums';
    private url = this.apiUrl + this.stagePath + this.resourcePath;

    constructor(private http: HttpClient) { }

    createAlbum(album: { title: string; releaseDate: string; genres: string[] }): Observable<any> {
        return this.http.post<any>(this.url, album);
    }

    getAlbums(): Observable<{ data: any[] }> {
        return this.http.get<{ data: any[] }>(this.url);
    }

    getAlbumsByGenre(genre: string): Observable<{ data: any[] }> {
        return this.http.get<{ data: any[] }>(`${this.url}/genre/${encodeURIComponent(genre)}`);
    }
}
