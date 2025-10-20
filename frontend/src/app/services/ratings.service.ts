import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../env/environment';

@Injectable({
    providedIn: 'root'
})
export class RatingsService {
    private baseUrl = `${environment.apiBaseUrl}/dev/ratings`;

    constructor(private http: HttpClient) { }

    getRatings(contentId: string): Observable<any> {
        return this.http.get(`${this.baseUrl}?contentId=${contentId}`);
    }

    getUserRating(userId: string, contentId: string): Observable<any> {
        return this.http.get(`${this.baseUrl}?contentId=${contentId}&userId=${userId}`);
    }

    createRating(userId: string, contentId: string, rating: string): Observable<any> {
        return this.http.post(this.baseUrl, { userId, contentId, rating });
    }

    deleteRating(userId: string, contentId: string): Observable<any> {
        return this.http.delete(`${this.baseUrl}?userId=${userId}&contentId=${contentId}`);
    }
}
