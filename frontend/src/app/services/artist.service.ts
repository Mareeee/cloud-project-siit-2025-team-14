import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Artist } from '../models/artist.model';

@Injectable({
    providedIn: 'root',
})
export class ArtistsService {
    private apiUrl = 'https://jbm2i4anqh.execute-api.eu-central-1.amazonaws.com';
    private stagePath = '/dev';
    private resourcePath = '/artists';
    private url = this.apiUrl + this.stagePath + this.resourcePath;

    constructor(private http: HttpClient) { }

    createArtist(artist: Omit<Artist, 'id'>): Observable<{ message: string; id: string }> {
        return this.http.post<{ message: string; id: string }>(this.url, artist);
    }

    getArtists(): Observable<{ data: Artist[] }> {
        return this.http.get<{ data: Artist[] }>(this.url);
    }

    getArtistsByGenre(genre: string): Observable<{ data: Artist[] }> {
        return this.http.get<{ data: Artist[] }>(`${this.url}/genre/${encodeURIComponent(genre)}`);
    }
}
