import { Component, OnInit } from '@angular/core';
import { GenresService } from '../services/genres.service';
import { Genre } from '../models/genre.model';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { DiscoverArtist, DiscoverAlbum, DiscoverSong } from '../models/discover.models';

@Component({
  selector: 'app-discover',
  templateUrl: './discover.component.html',
  styleUrls: ['./discover.component.css']
})
export class DiscoverComponent implements OnInit {
  availableGenres: string[] = [];
  selectedGenre: string | null = null;

  artists: DiscoverArtist[] = [];
  albums: DiscoverAlbum[] = [];
  songs: DiscoverSong[] = [];

  songSectionTitle = '';
  activeAudio: HTMLAudioElement | null = null;

  isLoading = false;

  constructor(
    private genresService: GenresService,
    private snackBar: MatSnackBar,
    private router: Router
  ) { }

  ngOnInit() {
    this.loadGenres();
  }

  loadGenres() {
    this.isLoading = true;
    this.genresService.getGenres().subscribe({
      next: (res) => {
        this.availableGenres = res.data.map((g: Genre) => g.name);
        if (this.availableGenres.length > 0) {
          this.selectedGenre = this.availableGenres[0];
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

  onGenreChange() {
    if (!this.selectedGenre) return;

    this.songSectionTitle = `Songs in ${this.selectedGenre}`;
    this.isLoading = true;

    this.genresService.getEntitiesByGenre(this.selectedGenre).subscribe({
      next: (res) => {
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
}
