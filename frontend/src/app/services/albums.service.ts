import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Album } from '../models/album.model';

@Injectable({
    providedIn: 'root'
})
export class AlbumsService {
    private apiUrl = 'https://jbm2i4anqh.execute-api.eu-central-1.amazonaws.com';
    private stagePath = '/dev';
    private resourcePath = '/albums';
    private url = this.apiUrl + this.stagePath + this.resourcePath;

    constructor(private http: HttpClient) { }

    createAlbum(album: Omit<Album, 'id'>): Observable<{ message: string; id: string }> {
        return this.http.post<{ message: string; id: string }>(this.url, album);
    }

    getAlbums(): Observable<{ data: Album[] }> {
        return this.http.get<{ data: Album[] }>(this.url);
    }

    getAlbumsByGenre(genre: string): Observable<{ data: Album[] }> {
        return this.http.get<{ data: Album[] }>(`${this.url}/genre/${encodeURIComponent(genre)}`);
    }
}
