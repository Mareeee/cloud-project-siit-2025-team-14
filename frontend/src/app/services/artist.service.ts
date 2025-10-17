import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class ArtistsService {
    private apiUrl = 'https://0ms84h98gd.execute-api.eu-central-1.amazonaws.com';
    private stagePath = '/dev';
    private resourcePath = '/artists';
    private url = this.apiUrl + this.stagePath + this.resourcePath;

    constructor(private http: HttpClient) { }

    createArtist(artist: { name: string; biography: string; genres: string[] }): Observable<any> {
        return this.http.post<any>(this.url, artist);
    }

    getArtists(): Observable<{ data: any[] }> {
        return this.http.get<{ data: any[] }>(this.url);
    }

    getArtistsByGenre(genre: string): Observable<{ data: any[] }> {
        return this.http.get<{ data: any[] }>(`${this.url}/genre/${encodeURIComponent(genre)}`);
    }
}
