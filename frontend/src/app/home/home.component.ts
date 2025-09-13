import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  constructor(
    private router: Router,
  ) { }

  goToContentOverview() {
    this.router.navigate(['/content-overview']);
  }

  goToArtistCreation() {
    this.router.navigate(['/artist-create']);
  }

  goToSongCreation() {
    this.router.navigate(['/song-create']);
  }
}
