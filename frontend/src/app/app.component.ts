import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { SongsService } from './song.service';
import { Artist } from './artist.model';
import { ArtistsService } from './artist.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
})
export class AppComponent {
  constructor(private http: HttpClient, private songsService: SongsService, private artistsService: ArtistsService) { }
  title = 'gateway-demo';
  response = 'The response will show up here';
  

  newArtist: Artist = { name: '', biography: '', genres: [] };

  showSongs() {
    this.songsService.getSongs().subscribe((res: any) => {
      this.response = JSON.stringify(res.data, null, 2);
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
        this.newArtist = { name: '', biography: '', genres: [] };
      },
      error: (err) => (this.response = 'Error: ' + JSON.stringify(err)),
    });
  }
}