import { Component, OnInit } from '@angular/core';
import { SongsService } from '../services/song.service';
import { ArtistsService } from '../services/artist.service';
import { AlbumsService } from '../services/albums.service';
import { GenresService } from '../services/genres.service';
import { Song } from '../models/song.model';
import { Artist } from '../models/artist.model';
import { Album } from '../models/album.model';
import { Genre } from '../models/genre.model';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-discover',
  templateUrl: './discover.component.html',
  styleUrls: ['./discover.component.css']
})
export class DiscoverComponent implements OnInit {
  availableGenres: string[] = [];
  selectedGenre: string | null = null;

  artists: Artist[] = [];
  albums: Album[] = [];
  songs: Song[] = [];

  songSectionTitle = '';
  activeAudio: HTMLAudioElement | null = null;

  isLoading = false;

  constructor(
    private songsService: SongsService,
    private artistsService: ArtistsService,
    private albumsService: AlbumsService,
    private genresService: GenresService,
    private snackBar: MatSnackBar
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

    this.artistsService.getArtistsByGenre(this.selectedGenre).subscribe({
      next: (res) => (this.artists = res.data || []),
      error: () => this.snackBar.open('Failed to load artists.', 'Close', { duration: 3000 })
    });

    this.albumsService.getAlbumsByGenre(this.selectedGenre).subscribe({
      next: (res) => (this.albums = res.data || []),
      error: () => this.snackBar.open('Failed to load albums.', 'Close', { duration: 3000 })
    });

    this.songsService.getSongsByGenre(this.selectedGenre).subscribe({
      next: (res) => {
        this.songs = (res.data || []).map((s: any) => ({
          ...s,
          isPlaying: false,
          currentTime: 0,
          duration: 0
        }));
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.snackBar.open('Failed to load songs.', 'Close', { duration: 3000 });
      }
    });
  }

  showArtistSongs(artistId: string) {
    this.songSectionTitle = 'Songs by selected artist';
    this.isLoading = true;

    this.songsService.getSongsByArtist(artistId).subscribe({
      next: (res) => {
        this.songs = (res.data || []).map((s: any) => ({
          ...s,
          isPlaying: false,
          currentTime: 0,
          duration: 0
        }));
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.snackBar.open('Failed to load artist songs.', 'Close', { duration: 3000 });
      }
    });
  }

  showAlbumSongs(albumId: string) {
    this.songSectionTitle = 'Songs from selected album';
    this.isLoading = true;

    this.songsService.getSongsByAlbum(albumId).subscribe({
      next: (res) => {
        this.songs = (res.data || []).map((s: any) => ({
          ...s,
          isPlaying: false,
          currentTime: 0,
          duration: 0
        }));
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.snackBar.open('Failed to load album songs.', 'Close', { duration: 3000 });
      }
    });
  }

  togglePlay(song: Song, audio: HTMLAudioElement) {
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

  seek(song: any, audio: HTMLAudioElement) {
    audio.currentTime = song.currentTime;
  }

  onLoadedMetadata(song: any, event: any) {
    song.duration = event.target.duration;
  }

  onTimeUpdate(song: any, event: any) {
    song.currentTime = event.target.currentTime;
  }

  formatTime(time: number) {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  }
}
