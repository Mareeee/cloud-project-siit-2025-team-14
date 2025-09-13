import { Component } from '@angular/core';
import { ArtistsService } from '../services/artist.service';
import { Artist } from '../models/artist.model';
import { AVAILABLE_GENRES } from '../utils/genres';

@Component({
  selector: 'app-artist-creation',
  templateUrl: './artist-creation.component.html',
  styleUrls: ['./artist-creation.component.css']
})
export class ArtistCreationComponent {
  newArtist: Artist = { id: '', name: '', biography: '', genres: [] };
  availableGenres = AVAILABLE_GENRES;
  dropdownOpen = false;

  showSnackbar = false;
  snackbarMessage = '';

  constructor(private artistsService: ArtistsService) { }

  toggleGenre(genre: string) {
    const index = this.newArtist.genres.indexOf(genre);
    if (index > -1) {
      this.newArtist.genres.splice(index, 1);
    } else {
      this.newArtist.genres.push(genre);
    }
  }

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  createArtist() {
    this.artistsService.createArtist(this.newArtist).subscribe({
      next: () => {
        this.triggerSnackbar('Artist created successfully!', true);
        this.newArtist = { id: '', name: '', biography: '', genres: [] };
      },
      error: (err) => {
        this.triggerSnackbar('Error creating artist: ' + err.message, false);
      }
    });
  }

  private triggerSnackbar(message: string, success: boolean) {
    this.snackbarMessage = message;
    this.showSnackbar = true;

    const snackbar = document.querySelector('.snackbar') as HTMLElement;
    if (snackbar) {
      snackbar.style.backgroundColor = success ? '#1f27cf' : '#b00020';
    }

    setTimeout(() => {
      this.showSnackbar = false;
    }, 3000);
  }
}
