import { Component } from '@angular/core';
import { SongsService } from '../song.service';
import { ArtistsService } from '../artist.service';
import { Song } from '../song.model';
import { Artist } from '../artist.model';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
})
export class HomeComponent {
  constructor(
    private songsService: SongsService,
    private artistsService: ArtistsService
  ) { }

  title = 'gateway-demo';
  response = 'The response will show up here';
  songs: any[] = [];
  currentSongUrl: string | null = null;

  newSong: Song = {
    title: 'New Song',
    id: "-1",
    artistIds: ["-1"],
    albumId: "-1",
    creationDate: "12.9.2025",
    genres: ["asdf"]
  };

  selectedCover!: File;
  selectedAudio!: File;
  newArtist: Artist = { id: '-1', name: '', biography: '', genres: [] };

  showSongs() {
    this.songsService.getSongs().subscribe((res: any) => {
      this.songs = res.data || [];
      this.response = JSON.stringify(res.data, null, 2);
    });
  }

  playSong(url: string) {
    this.currentSongUrl = url;
  }

  onCoverSelected(event: any) {
    this.selectedCover = event.target.files[0];
  }

  onAudioSelected(event: any) {
    this.selectedAudio = event.target.files[0];
  }

  addSong() {
    this.songsService.addSong(this.newSong, this.selectedCover, this.selectedAudio).subscribe({
      next: (res) => this.response = 'Success: ' + JSON.stringify(res),
      error: (err) => this.response = 'Error: ' + JSON.stringify(err)
    });
  }

  createArtist() {
    const genresArray = this.newArtist.genres;
    this.artistsService.createArtist({
      name: this.newArtist.name,
      biography: this.newArtist.biography,
      genres: genresArray,
    }).subscribe({
      next: (res) => {
        this.response = 'Artist created: ' + JSON.stringify(res);
        this.newArtist = { id: '-1', name: '', biography: '', genres: [] };
      },
      error: (err) => (this.response = 'Error: ' + JSON.stringify(err)),
    });
  }
}
