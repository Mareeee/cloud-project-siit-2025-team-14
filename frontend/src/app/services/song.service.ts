import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin } from 'rxjs';
import { Song } from '../models/song.model';
import { environment } from '../../env/environment';
import { set, get, del, keys } from 'idb-keyval';

@Injectable({
  providedIn: 'root',
})
export class SongsService {
  private stagePath = '/dev';
  private resourcePath = '/songs';
  private url = environment.apiBaseUrl + this.stagePath + this.resourcePath;

  constructor(private http: HttpClient) { }

  getSongs(): Observable<{ data: Song[] }> {
    return this.http.get<{ data: Song[] }>(this.url);
  }

  addSong(song: Song, cover: File, audio: File): Observable<any> {
    return new Observable((observer) => {
      this.http
        .put<any>(this.url, {
          title: song.title,
          albumId: song.albumId,
          artistIds: song.artistIds,
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

  deleteSong(songId: string) {
    return this.http.delete<void>(`${this.url}/${songId}`);
  }

  getSongsByGenre(genre: string): Observable<{ data: Song[] }> {
    return this.http.get<{ data: Song[] }>(`${this.url}/genre/${encodeURIComponent(genre)}`);
  }

  getSongsByArtist(artistId: string): Observable<{ data: Song[] }> {
    return this.http.get<{ data: Song[] }>(`${this.url}/artist/${artistId}`);
  }

  getSongsByAlbum(albumId: string): Observable<{ data: Song[] }> {
    return this.http.get<{ data: Song[] }>(`${this.url}/album/${albumId}`);
  }

  getDownloadUrl(songId: string, title: string): Observable<{ downloadUrl: string }> {
    const encodedTitle = encodeURIComponent(title);
    const url = `${this.url}/download/${songId}/${encodedTitle}`;
    return this.http.get<{ downloadUrl: string }>(url);
  }

  async saveSongOffline(songId: string, title: string, blob: Blob) {
    try {
      await set(`offline-song-${songId}`, { id: songId, title, blob });
      console.log(`Saved "${title}" to IndexedDB.`);
    } catch (err) {
      console.error('Failed to save offline song:', err);
    }
  }

  async getOfflineSongs(): Promise<{ id: string; title: string; blob: Blob }[]> {
    const allKeys = await keys();
    const offlineKeys = allKeys.filter(k => typeof k === 'string' && k.startsWith('offline-song-'));
    const songs = [];
    for (const key of offlineKeys) {
      const value = await get(key);
      if (value) songs.push(value);
    }
    return songs;
  }

  async getOfflineSong(id: string): Promise<Blob | null> {
    const data = await get(`offline-song-${id}`);
    return data?.blob || null;
  }

  async deleteOfflineSong(id: string) {
    await del(`offline-song-${id}`);
    console.log(`Deleted offline song ${id} from IndexedDB.`);
  }

}
