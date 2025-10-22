import { Component, OnInit, OnDestroy } from '@angular/core';
import { FeedService } from '../../services/feed.service';
import { FeedItem } from '../../models/feed.model';

import { fromEvent, interval, merge, Subject } from 'rxjs';
import { filter, takeUntil } from 'rxjs/operators';
import { Artist } from '../../models/artist.model';

@Component({
  selector: 'app-feed',
  templateUrl: './feed.component.html',
  styleUrls: ['./feed.component.css']
})
export class FeedPageComponent implements OnInit, OnDestroy {
  loading = false;
  error: string | null = null;
  items: FeedItem[] = [];

  private destroy$ = new Subject<void>();
  private readonly REFRESH_MS = 90000;

  constructor(private feedService: FeedService) { }

  ngOnInit(): void {
    this.loadFeed();
    this.startAutoRefresh();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadFeed(): void {
    this.loading = true;
    this.error = null;

    this.feedService.getFeed().subscribe({
      next: (items) => {
        this.items = items;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Something went wrong. Try again.';
      }
    });
  }

  refresh(): void {
    this.loadFeed();
  }

  private startAutoRefresh(): void {
    const onFocus$ = fromEvent(document, 'visibilitychange').pipe(
      filter(() => document.visibilityState === 'visible')
    );

    const intervalWhileVisible$ = interval(this.REFRESH_MS).pipe(
      filter(() => document.visibilityState === 'visible')
    );

    merge(onFocus$, intervalWhileVisible$)
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.loadFeed();
      });
  }

  onPlay(songId: string): void {
    console.log('Play song', songId);
  }

  openAlbum(albumId: string): void {
    console.log('Open album', albumId);
  }

  openArtist(artistId: string): void {
    console.log('Open artist', artistId);
  }

  truncate(bio?: string): string {
    if (!bio) return '';
    return bio.length > 160 ? bio.slice(0, 160) + '…' : bio;
  }

  genresLabel(artist?: Artist): string {
    const g = artist?.genres;
    return g && g.length ? g.join(', ') : 'Artist';
  }

  trackByItem = (_: number, it: any) => {
    if (it.type === 'SONG') return `SONG-${it.song.id}`;
    if (it.type === 'ALBUM') return `ALBUM-${it.album.id}`;
    if (it.type === 'ARTIST') return `ARTIST-${it.artist.id}`;
    return _;
  };
}
