import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin } from 'rxjs';
import { Song } from './music.model';

@Injectable({
  providedIn: 'root',
})
export class SongsService {
  constructor(private http: HttpClient) {}

  private apiUrl = 'https://35500nafx8.execute-api.eu-central-1.amazonaws.com';
  private stagePath = '/dev';
  private resourcePath = '/songs';

  private url = this.apiUrl + this.stagePath + this.resourcePath;

  getSongs(): Observable<Song[]> {
    return this.http.get<Song[]>(this.url);
  }

  addSong(song: Song, cover: File, audio: File): Observable<any> {
    return new Observable((observer) => {
      this.http
        .put<any>(this.url, {
          title: song.title,
          authorId: song.authorId,
          genres: song.genres,
          coverFilename: cover.name,
          audioFilename: audio.name,
        })
        .subscribe({
          next: (res) => {
            const coverUpload$ = this.http.put(res.coverUploadUrl, cover, {
              headers: { 'Content-Type': cover.type },
            });

            const audioUpload$ = this.http.put(res.audioUploadUrl, audio, {
              headers: { 'Content-Type': audio.type },
            });

            forkJoin([coverUpload$, audioUpload$]).subscribe({
              next: () => {
                observer.next({
                  message: 'Song Added',
                  id: res.id,
                  title: song.title,
                });
                observer.complete();
              },
              error: (err) => observer.error(err),
            });
          },
          error: (err) => observer.error(err),
        });
    });
  }
}
