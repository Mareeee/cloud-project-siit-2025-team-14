import { Component, OnInit } from '@angular/core';
import { GenresService } from '../services/genres.service';
import { Genre } from '../models/genre.model';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { DiscoverArtist, DiscoverAlbum, DiscoverSong } from '../models/discover.models';
import { SubscriptionsService } from '../services/subscriptions.service';
import { AuthService } from '../auth/auth.service';
import { CreateSubscription } from '../models/create-subscription.model';
import { SongsService } from '../services/song.service';

@Component({
  selector: 'app-discover',
  templateUrl: './discover.component.html',
  styleUrls: ['./discover.component.css']
})
export class DiscoverComponent implements OnInit {
  availableGenres: Genre[] = [];
  selectedGenre: string | null = null;

  artists: DiscoverArtist[] = [];
  albums: DiscoverAlbum[] = [];
  songs: DiscoverSong[] = [];

  songSectionTitle = '';
  activeAudio: HTMLAudioElement | null = null;

  isLoading = false;

  subscriptionsMap: Record<string, boolean> = {};
  subscriptionsLoaded = false;

  constructor(
    private genresService: GenresService,
    private snackBar: MatSnackBar,
    private router: Router,
    private subscriptionsService: SubscriptionsService,
    private authService: AuthService,
    private songsService: SongsService
  ) { }

  ngOnInit() {
    this.loadGenres();
    this.loadUserSubscriptions();
  }

  async loadUserSubscriptions() {
    const userId = await this.authService.getUserId();
    if (!userId) return;

    this.subscriptionsService.getSubscriptions(userId).subscribe({
      next: (res) => {
        res.data.forEach((sub: any) => {
          this.subscriptionsMap[sub.targetName] = true;
        });
        this.subscriptionsLoaded = true;
      },
      error: (err) => {
        console.error('Failed to load subscriptions', err);
        this.subscriptionsLoaded = true;
      }
    });
  }

  loadGenres() {
    this.isLoading = true;
    this.genresService.getGenres().subscribe({
      next: (res) => {
        this.availableGenres = res.data;
        if (this.availableGenres.length > 0) {
          this.selectedGenre = this.availableGenres[0].name;
          this.onGenreChange();
        }
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.snackBar.open('Failed to load genres.', 'Close', { duration: 3000 });
      }
    });
  }

  async onGenreChange() {
    if (!this.selectedGenre) return;

    this.songSectionTitle = `Songs in ${this.selectedGenre}`;
    this.isLoading = true;

    this.genresService.getEntitiesByGenre(this.selectedGenre).subscribe({
      next: async (res) => {
        const data = res.data || [];

        this.artists = data.filter((item: any) => item.entityType === 'ARTIST');
        this.albums = data.filter((item: any) => item.entityType === 'ALBUM');
        this.songs = data
          .filter((item: any) => item.entityType === 'SONG')
          .map((s: DiscoverSong) => ({
            ...s,
            isPlaying: false,
            currentTime: 0,
            duration: 0
          }));

        for (const song of this.songs) {
          const blob = await this.songsService.getOfflineSong(song.entityId);
          if (blob) {
            song.audioUrl = URL.createObjectURL(blob);
            song.isOffline = true;
          }
        }

        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.snackBar.open('Failed to load data by genre.', 'Close', { duration: 3000 });
      }
    });
  }

  showArtistSongs(artistId: string) {
    this.router.navigate(['/content-overview'], { queryParams: { artistId } });
  }

  showAlbumSongs(albumId: string) {
    this.router.navigate(['/content-overview'], { queryParams: { albumId } });
  }

  togglePlay(song: DiscoverSong, audio: HTMLAudioElement) {
    if (!navigator.onLine && !song.audioUrl?.startsWith('blob:')) {
      this.snackBar.open(`No internet - cannot stream "${song.title}"`, 'Close', { duration: 3000 });
      return;
    }

    if (this.activeAudio && this.activeAudio !== audio) {
      this.activeAudio.pause();
      const prev = this.songs.find(s => s.audioUrl === this.activeAudio?.src);
      if (prev) prev.isPlaying = false;
    }

    if (song.isPlaying) {
      audio.pause();
      song.isPlaying = false;
      this.activeAudio = null;
    } else {
      if (song.audioUrl?.startsWith('blob:')) {
        console.log(`Playing from LOCAL STORAGE: ${song.title}`);
      } else {
        console.log(`Streaming from AWS: ${song.title}`);
      }

      audio.play();
      song.isPlaying = true;
      this.activeAudio = audio;
    }
  }

  seek(song: DiscoverSong, audio: HTMLAudioElement) {
    audio.currentTime = song.currentTime!;
  }

  onLoadedMetadata(song: DiscoverSong, event: any) {
    song.duration = event.target.duration;
  }

  onTimeUpdate(song: DiscoverSong, event: any) {
    song.currentTime = event.target.currentTime;
  }

  formatTime(time: number) {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  }

  isSubscribed(targetName: string): boolean {
    return !!this.subscriptionsMap[targetName];
  }

  async toggleSubscription(targetName: string, targetId: string, targetType: string) {
    const userId = await this.authService.getUserId();
    const userEmail = (await this.authService.getUserEmail());

    if (!userId || !userEmail) {
      this.snackBar.open('You must be logged in to subscribe.', 'Close', { duration: 3000 });
      return;
    }

    if (this.isSubscribed(targetName)) {
      const subscriptionId = await this.getSubscriptionIdByTarget(targetName);
      if (!subscriptionId) return;

      this.subscriptionsService.deleteSubscription(subscriptionId).subscribe({
        next: () => {
          this.snackBar.open('Unsubscribed successfully', 'Close', { duration: 3000 });
          delete this.subscriptionsMap[targetName];
        },
        error: (err) => {
          console.error('Failed to unsubscribe', err);
          this.snackBar.open('Failed to unsubscribe', 'Close', { duration: 3000 });
        }
      });
    } else {
      const payload: CreateSubscription = { userId, targetId, targetType, email: userEmail };
      this.subscriptionsService.createSubscription(payload).subscribe({
        next: (res: any) => {
          this.snackBar.open('Subscribed successfully', 'Close', { duration: 3000 });
          this.subscriptionsMap[targetName] = true;
        },
        error: (err) => {
          console.error('Failed to subscribe', err);
          this.snackBar.open('Failed to subscribe', 'Close', { duration: 3000 });
        }
      });
    }
  }

  async getSubscriptionIdByTarget(targetName: string): Promise<string | null> {
    const userId = await this.authService.getUserId();
    if (!userId) return null;

    return new Promise((resolve) => {
      this.subscriptionsService.getSubscriptions(userId).subscribe({
        next: (res) => {
          const sub = res.data.find((s: any) => s.targetName === targetName);
          resolve(sub ? String(sub.subscriptionId) : null);
        },
        error: () => resolve(null)
      });
  }  
      
  downloadSong(song: DiscoverSong) {
    this.songsService.getDownloadUrl(song.entityId, song.title).subscribe({
      next: (res) => {
        const link = document.createElement('a');
        link.href = res.downloadUrl;
        link.download = `${song.title}.mp3`;
        link.click();
      },
      error: (err) => {
        console.error('Failed to get download URL:', err);
        this.snackBar.open('Failed to download song.', 'Close', { duration: 3000 });
      },
    });
  }

  async downloadOffline(song: DiscoverSong) {
    if (song.isOffline) {
      await this.songsService.deleteOfflineSong(song.entityId);
      this.snackBar.open(`Offline copy removed for "${song.title}"`, 'Close', { duration: 3000 });
      return;
    }

    this.songsService.getDownloadUrl(song.entityId, song.title).subscribe({
      next: async (res) => {
        const response = await fetch(res.downloadUrl);
        const blob = await response.blob();
        await this.songsService.saveSongOffline(song.entityId, song.title, blob);
        this.snackBar.open(`"${song.title}" is now available offline!`, 'Close', { duration: 3000 });
      },
      error: () => {
        this.snackBar.open('Failed to get download URL.', 'Close', { duration: 3000 });
      }
    });
  }
}
