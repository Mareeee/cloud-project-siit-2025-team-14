import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SongsService } from '../services/song.service';
import { ArtistsService } from '../services/artist.service';
import { forkJoin } from 'rxjs';
import { Song } from '../models/song.model';
import { Artist } from '../models/artist.model';
import { AuthService } from '../auth/auth.service';
import { RatingsService } from '../services/ratings.service';

@Component({
  selector: 'app-content-overview',
  templateUrl: './content-overview.component.html',
  styleUrls: ['./content-overview.component.css']
})
export class ContentOverviewComponent implements OnInit {
  songs: Song[] = [];
  artists: Artist[] = [];
  activeAudio: HTMLAudioElement | null = null;
  title: string = 'All Songs';
  isLoading = false;
  currentUserId: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private songsService: SongsService,
    private artistsService: ArtistsService,
    private ratingsService: RatingsService,
    private authService: AuthService
  ) { }

  async ngOnInit() {
    this.currentUserId = await this.authService.getUserId();

    this.route.queryParams.subscribe(params => {
      const artistId = params['artistId'];
      const albumId = params['albumId'];

      this.isLoading = true;

      if (artistId) {
        this.title = 'Songs by Selected Artist';
        this.loadSongsByArtist(artistId);
      } else if (albumId) {
        this.title = 'Songs from Selected Album';
        this.loadSongsByAlbum(albumId);
      } else {
        this.title = 'All Songs';
        this.loadAllSongs();
      }
    });
  }

  private loadSongsByArtist(artistId: string) {
    forkJoin({
      songs: this.songsService.getSongsByArtist(artistId),
      artists: this.artistsService.getArtists()
    }).subscribe(({ songs, artists }) => {
      this.setSongsWithArtists(songs.data || [], artists.data || []);
      this.isLoading = false;
    });
  }

  private loadSongsByAlbum(albumId: string) {
    forkJoin({
      songs: this.songsService.getSongsByAlbum(albumId),
      artists: this.artistsService.getArtists()
    }).subscribe(({ songs, artists }) => {
      this.setSongsWithArtists(songs.data || [], artists.data || []);
      this.isLoading = false;
    });
  }

  private loadAllSongs() {
    forkJoin({
      songs: this.songsService.getSongs(),
      artists: this.artistsService.getArtists()
    }).subscribe(({ songs, artists }) => {
      this.setSongsWithArtists(songs.data || [], artists.data || []);
      this.isLoading = false;
    });
  }

  private setSongsWithArtists(songs: any[], artists: Artist[]) {
    this.songs = songs.map((song: any) => {
      const songArtists = artists.filter(a => song.artistIds?.includes(a.id));
      return {
        ...song,
        id: song.id || song.entityId || song.songId,
        artistNames: songArtists.map(a => a.name),
        artistBios: songArtists.map(a => a.biography),
        artistGenres: songArtists.flatMap(a => a.genres),
        isPlaying: false,
        currentTime: 0,
        duration: 0,
        averageRating: null,
        userRating: null
      };
    });

    this.songs.forEach(song => {
      this.ratingsService.getRatings(song.id).subscribe(res => {
        song.averageRating = res.averageRating;
      });

      if (this.currentUserId) {
        this.ratingsService.getUserRating(this.currentUserId, song.id).subscribe(res => {
          song.userRating = res.userRating;
        });
      }
    });
  }

  rateSong(song: Song, rating: 'love' | 'like' | 'dislike') {
    if (!this.currentUserId) {
      alert('You must be logged in to rate songs.');
      return;
    }

    const isSameRating = song.userRating === rating;

    if (isSameRating) {
      this.ratingsService.deleteRating(this.currentUserId, song.id).subscribe({
        next: () => {
          song.userRating = null;
          this.refreshAverage(song);
        },
        error: () => alert('Failed to delete rating.')
      });
    } else {
      this.ratingsService.createRating(this.currentUserId, song.id, rating).subscribe({
        next: () => {
          song.userRating = rating;
          this.refreshAverage(song);
        },
        error: () => alert('Failed to save rating.')
      });
    }
  }

  private refreshAverage(song: Song) {
    this.ratingsService.getRatings(song.id).subscribe(res => {
      song.averageRating = res.averageRating;
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
