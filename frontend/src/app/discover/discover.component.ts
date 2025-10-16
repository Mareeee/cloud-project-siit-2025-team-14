import { Component } from '@angular/core';
import { SongsService } from '../services/song.service';
import { ArtistsService } from '../services/artist.service';
import { AlbumsService } from '../services/albums.service';
import { Song } from '../models/song.model';
import { Artist } from '../models/artist.model';
import { Album } from '../models/album.model';

@Component({
  selector: 'app-discover',
  templateUrl: './discover.component.html',
  styleUrls: ['./discover.component.css']
})
export class DiscoverComponent {
  availableGenres = [
    'Rock', 'Pop', 'Jazz', 'Hip-Hop', 'Classical',
    'Country', 'Electronic', 'Reggae', 'Metal', 'Blues'
  ];
  selectedGenre = this.availableGenres[0];

  artists: Artist[] = [];
  albums: Album[] = [];
  songs: Song[] = [];
  songSectionTitle = 'Songs';

  activeAudio: HTMLAudioElement | null = null;

  constructor(
    private songsService: SongsService,
    private artistsService: ArtistsService,
    private albumsService: AlbumsService
  ) { }

  onGenreChange() {
    this.songSectionTitle = `Songs in ${this.selectedGenre}`;
    this.loadGenreData();
  }

  ngOnInit() {
    this.loadGenreData();
  }

  loadGenreData() {
    this.artistsService.getArtistsByGenre(this.selectedGenre).subscribe(res => this.artists = res.data || []);
    this.albumsService.getAlbumsByGenre(this.selectedGenre).subscribe(res => this.albums = res.data || []);
    // this.songsService.getSongsByGenre(this.selectedGenre).subscribe(res => {
    //   this.songs = (res.data || []).map((s: any) => ({
    //     ...s,
    //     isPlaying: false,
    //     currentTime: 0,
    //     duration: 0
    //   }));
    // });
  }

  showArtistSongs(artistId: string) {
    this.songSectionTitle = 'Songs by selected artist';
    this.songsService.getSongsByArtist(artistId).subscribe(res => {
      this.songs = (res.data || []).map((s: any) => ({
        ...s,
        isPlaying: false,
        currentTime: 0,
        duration: 0
      }));
    });
  }

  showAlbumSongs(albumId: string) {
    this.songSectionTitle = 'Songs from selected album';
    this.songsService.getSongsByAlbum(albumId).subscribe(res => {
      this.songs = (res.data || []).map((s: any) => ({
        ...s,
        isPlaying: false,
        currentTime: 0,
        duration: 0
      }));
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
