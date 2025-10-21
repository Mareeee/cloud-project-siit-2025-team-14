import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Album } from '../models/album.model';
import { environment } from '../../env/environment';

@Injectable({
    providedIn: 'root'
})
export class AlbumsService {
    private stagePath = '/dev';
    private resourcePath = '/albums';
    private url = environment.apiBaseUrl + this.stagePath + this.resourcePath;

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

    editAlbum(albumId: string, patch: Partial<Album>) {
        return this.http.put<{ message: string }>(
            `${this.url}/${encodeURIComponent(albumId)}`,
            patch
        );
    }

    deleteAlbum(albumId: string) {
        return this.http.delete<{ message: string }>(
            `${this.url}/${encodeURIComponent(albumId)}`
        );
    }

}