import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { SongsService } from './song.service';
import { Song } from './music.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
})
export class AppComponent {
  constructor(private http: HttpClient, private songsService: SongsService) { }
  title = 'gateway-demo';
  response = 'The response will show up here';
  newSong: Song = { title: 'New Song' };
  selectedFile?: File;

  showSongs() {
    this.songsService.getSongs().subscribe((res: any) => {
      this.response = JSON.stringify(res.data, null, 2);
    });
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  addSong() {
    this.songsService.addSong(this.newSong, this.selectedFile).subscribe({
      next: (res) => this.response = 'Success: ' + JSON.stringify(res),
      error: (err) => this.response = 'Error: ' + JSON.stringify(err)
    });
  }
}