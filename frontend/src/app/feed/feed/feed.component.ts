import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { Subject } from 'rxjs';

import { FeedService, FeedBuckets } from '../../services/feed.service';
import { Artist } from '../../models/artist.model';
import { AuthService } from '../../auth/auth.service';
import { SongFeedItem, AlbumFeedItem, ArtistFeedItem } from '../../models/feed.model';

type UiState = {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
};

@Component({
  selector: 'app-feed',
  templateUrl: './feed.component.html',
  styleUrls: ['./feed.component.css']
})
export class FeedPageComponent implements OnInit, OnDestroy {
  loading = false;
  error: string | null = null;

  songs: SongFeedItem[] = [];
  artists: ArtistFeedItem[] = [];
  albums: AlbumFeedItem[] = [];

  get totalCount(): number {
    return (this.songs?.length || 0) + (this.artists?.length || 0) + (this.albums?.length || 0);
  }

  currentUserId: string | null = null;
  private destroy$ = new Subject<void>();

  ui: Partial<Record<string, UiState>> = {};
  private activeAudio: HTMLAudioElement | null = null;
  private activeSongId: string | null = null;

  constructor(
    private feedService: FeedService,
    private authService: AuthService,
    private router: Router
  ) { }

  async ngOnInit() {
    this.currentUserId = await this.authService.getUserId();
    this.loadFeed();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();

    if (this.activeAudio) {
      try { this.activeAudio.pause(); } catch { }
      this.activeAudio = null;
      this.activeSongId = null;
    }
  }

  loadFeed(): void {
    this.loading = true;
    this.error = null;

    this.feedService.getFeed(this.currentUserId!).subscribe({
      next: (feed: FeedBuckets) => {
        this.songs = Array.isArray(feed?.songs) ? feed.songs : [];
        this.artists = Array.isArray(feed?.artists) ? feed.artists : [];
        this.albums = Array.isArray(feed?.albums) ? feed.albums : [];

        const map: Record<string, UiState> = {};
        for (const it of this.songs) {
          if (!it?.song?.id) continue;
          map[it.song.id] = { isPlaying: false, currentTime: 0, duration: 0 };
        }
        this.ui = map;

        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.loading = false;
        this.error = 'Something went wrong. Try again.';
      }
    });
  }

  refresh(): void { this.loadFeed(); }

  discover() {
    this.router.navigate(['/discover']);
  }

  async togglePlay(songId: string, audio: HTMLAudioElement, title: string) {
    if (this.activeAudio && this.activeAudio !== audio) {
      try { this.activeAudio.pause(); } catch { }
      if (this.activeSongId && this.ui[this.activeSongId]) {
        this.ui[songId] ??= { isPlaying: false, currentTime: 0, duration: 0 };
      }
    }

    if (this.activeAudio === audio && this.ui[songId]?.isPlaying) {
      audio.pause();
      this.ui[songId].isPlaying = false;
      this.activeAudio = null;
      this.activeSongId = null;
      return;
    }

    await audio.play();
    this.ui[songId] ??= { isPlaying: false, currentTime: 0, duration: 0 };
    this.ui[songId].isPlaying = true;
    this.activeAudio = audio;
    this.activeSongId = songId;

    if (navigator.onLine && this.currentUserId) {
      this.feedService.listenSong(this.currentUserId, songId).subscribe({
        next: () => { },
        error: (err) => console.warn('listenSong failed:', err)
      });
    }

    console.log(`Playing: ${title}`);
  }

  onLoadedMetadata(songId: string, ev: Event) {
    const a = ev.target as HTMLAudioElement;
    this.ui[songId] ??= { isPlaying: false, currentTime: 0, duration: 0 };
    this.ui[songId].duration = a.duration || 0;
  }

  onTimeUpdate(songId: string, ev: Event) {
    const a = ev.target as HTMLAudioElement;
    this.ui[songId] ??= { isPlaying: false, currentTime: 0, duration: 0 };
    this.ui[songId].currentTime = a.currentTime || 0;
  }

  onEnded(songId: string) {
    if (this.ui[songId]) this.ui[songId].isPlaying = false;
    this.activeAudio = null;
    this.activeSongId = null;
  }

  seek(songId: string, audio: HTMLAudioElement, val: number) {
    const t = Number(val ?? 0);
    audio.currentTime = isFinite(t) ? t : 0;
    this.ui[songId] ??= { isPlaying: false, currentTime: 0, duration: 0 };
    this.ui[songId].currentTime = audio.currentTime;
  }

  formatTime(time: number) {
    const minutes = Math.floor((time || 0) / 60);
    const seconds = Math.floor((time || 0) % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  }

  openAlbum(albumId?: string): void {
    if (!albumId) return;
    this.router.navigate(['/content-overview'], { queryParams: { albumId } });
  }

  openAlbumFromSong(albumId?: string): void { this.openAlbum(albumId); }

  openArtist(artistId?: string): void {
    if (!artistId) return;
    this.router.navigate(['/content-overview'], { queryParams: { artistId } });
  }

  truncate(bio?: string): string {
    if (!bio) return '';
    return bio.length > 160 ? bio.slice(0, 160) + '…' : bio;
  }

  genresLabel(artist?: Artist): string {
    const g = artist?.genres;
    return g && g.length ? g.join(', ') : 'Artist';
  }

  trackByItem = (_: number, it: SongFeedItem | AlbumFeedItem | ArtistFeedItem) => {
    if (it?.type === 'SONG') return `SONG-${it.song?.id}`;
    if (it?.type === 'ALBUM') return `ALBUM-${it.album?.id}`;
    if (it?.type === 'ARTIST') return `ARTIST-${it.artist?.id}`;
    return _;
  };
}
