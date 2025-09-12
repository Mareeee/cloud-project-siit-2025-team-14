import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Song } from './music.model';

@Injectable({
    providedIn: 'root',
})
export class SongsService {
    constructor(private http: HttpClient) { }

    private apiUrl = 'https://35500nafx8.execute-api.eu-central-1.amazonaws.com';
    private stagePath = '/dev';
    private resourcePath = '/songs';

    private url = this.apiUrl + this.stagePath + this.resourcePath;

    getSongs(): Observable<Song[]> {
        return this.http.get<Song[]>(this.url);
    }

    addSong(song: Song, file?: File): Observable<any> {
        if (!file) {
            throw new Error('File Required!');
        }

        return new Observable((observer) => {
            this.http.put<any>(this.url, {
                title: song.title,
                filename: file.name
            }).subscribe({
                next: (res) => {
                    const uploadUrl = res.uploadUrl;

                    this.http.put(uploadUrl, file, {
                        headers: { 'Content-Type': file.type }
                    }).subscribe({
                        next: () => {
                            observer.next({
                                message: 'Song Added',
                                id: res.id,
                                title: song.title
                            });
                            observer.complete();
                        },
                        error: (err) => observer.error(err)
                    });
                },
                error: (err) => observer.error(err)
            });
        });
    }
}