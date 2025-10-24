import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Artist } from '../models/artist.model';
import { environment } from '../../env/environment';

@Injectable({
    providedIn: 'root',
})
export class ArtistsService {
    private stagePath = '/dev';
    private resourcePath = '/artists';
    private url = environment.apiBaseUrl + this.stagePath + this.resourcePath;

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

    deleteArtist(artistId: string): Observable<boolean> {
        return this.http.delete<boolean>(`${this.url}/${artistId}`)
    }

    editArtist(artist: Artist): Observable<any> {
        return this.http.put<any>(`${this.url}/${artist.id}`, { biography: artist.biography, genreIds: artist.genreIds })
    }
}