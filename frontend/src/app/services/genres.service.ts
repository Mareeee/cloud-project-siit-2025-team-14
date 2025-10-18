import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Genre } from '../models/genre.model';

@Injectable({
    providedIn: 'root'
})
export class GenresService {
    private apiUrl = 'https://0ms84h98gd.execute-api.eu-central-1.amazonaws.com';
    private stagePath = '/dev';
    private resourcePath = '/genres';
    private url = this.apiUrl + this.stagePath + this.resourcePath;

    constructor(private http: HttpClient) { }

    getGenres(): Observable<{ data: Genre[] }> {
        return this.http.get<{ data: Genre[] }>(this.url);
    }
}
