import { Component } from '@angular/core';
import { SongsService } from '../services/song.service';
import { ArtistsService } from '../services/artist.service';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-content-overview',
  templateUrl: './content-overview.component.html',
  styleUrls: ['./content-overview.component.css']
})
export class ContentOverviewComponent {
  songs: any[] = [];
  artists: any[] = [];

  constructor(
    private songsService: SongsService,
    private artistsService: ArtistsService,
  ) {
    forkJoin({
      songs: this.songsService.getSongs(),
      artists: this.artistsService.getArtists()
    }).subscribe(({ songs, artists }) => {
      this.artists = artists.data || [];

      this.songs = (songs.data || []).map((song: any) => {
        const artist = this.artists.find(a => a.id === song.artistId);
        return {
          ...song,
          artistName: artist ? artist.name : 'Unknown Artist',
          artistBio: artist ? artist.biography : '',
          artistGenres: artist ? artist.genres : [],
          isPlaying: false,
          currentTime: 0,
          duration: 0
        };
      });
    });
  }

  togglePlay(song: any) {
    const audio: HTMLAudioElement = document.querySelector(`audio[src="${song.audioUrl}"]`)!;
    if (!audio) return;

    if (song.isPlaying) {
      audio.pause();
      song.isPlaying = false;
    } else {
      audio.play();
      song.isPlaying = true;
    }
  }

  seek(song: any) {
    const audio: HTMLAudioElement = document.querySelector(`audio[src="${song.audioUrl}"]`)!;
    audio.currentTime = song.currentTime;
  }

  onLoadedMetadata(event: any, song: any) {
    song.duration = event.target.duration;
  }

  onTimeUpdate(event: any, song: any) {
    song.currentTime = event.target.currentTime;
  }

  formatTime(time: number) {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  }
}
