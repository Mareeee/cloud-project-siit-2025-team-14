import { Component } from '@angular/core';
import { SongsService } from '../services/song.service';
import { ArtistsService } from '../services/artist.service';
import { forkJoin } from 'rxjs';
import { Song } from '../models/song.model';
import { Artist } from '../models/artist.model';

@Component({
  selector: 'app-content-overview',
  templateUrl: './content-overview.component.html',
  styleUrls: ['./content-overview.component.css']
})
export class ContentOverviewComponent {
  songs: Song[] = [];
  artists: Artist[] = [];
  activeAudio: HTMLAudioElement | null = null;

  constructor(
    private songsService: SongsService,
    private artistsService: ArtistsService,
  ) {
    forkJoin({
      artists: this.artistsService.getArtists(),
      songs: this.songsService.getSongs(),
    }).subscribe(({ songs, artists }) => {
      this.artists = artists.data || [];

      this.songs = (songs.data || []).map((song: any) => {
        const songArtists = this.artists.filter(a => song.artistIds.includes(a.id));
        return {
          ...song,
          artistNames: songArtists.map(a => a.name),
          artistBios: songArtists.map(a => a.biography),
          artistGenres: songArtists.flatMap(a => a.genres),
          isPlaying: false,
          currentTime: 0,
          duration: 0
        };
      });
    });
  }

  togglePlay(song: Song, audio: HTMLAudioElement) {
    if (this.activeAudio && this.activeAudio !== audio) {
      this.activeAudio.pause();
      const prevSong = this.songs.find(s => s.audioUrl === this.activeAudio?.src);
      if (prevSong) prevSong.isPlaying = false;
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
