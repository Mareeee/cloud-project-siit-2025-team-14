import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class ArtistsService {
    constructor(private http: HttpClient) { }

    private apiUrl = 'https://35500nafx8.execute-api.eu-central-1.amazonaws.com';
    private stagePath = '/dev';
    private resourcePath = '/artists';

    private url = this.apiUrl + this.stagePath + this.resourcePath;

    createArtist(artist: { name: string; biography: string; genres: string[] }): Observable<any> {
        return this.http.post<any>(this.url, artist);
    }
}