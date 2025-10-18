import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AlbumsService } from '../services/albums.service';
import { ArtistsService } from '../services/artist.service';
import { GenresService } from '../services/genres.service';
import { Album } from '../models/album.model';
import { Artist } from '../models/artist.model';
import { Genre } from '../models/genre.model';

@Component({
  selector: 'app-albums-creation',
  templateUrl: './albums-creation.component.html',
  styleUrls: ['./albums-creation.component.css']
})
export class AlbumsCreationComponent implements OnInit {
  newAlbum: Album = { id: '', title: '', releaseDate: '', genres: [] };
  availableArtists: Artist[] = [];
  availableGenres: string[] = [];

  artistDropdownOpen = false;
  genreDropdownOpen = false;
  selectedArtistIds: string[] = [];
  createFullAlbum = false;

  touched = { title: false, releaseDate: false, genres: false };

  showSnackbar = false;
  snackbarMessage = '';

  constructor(
    private albumsService: AlbumsService,
    private artistsService: ArtistsService,
    private genresService: GenresService,
    private router: Router
  ) { }

  ngOnInit() {
    this.loadArtists();
    this.loadGenres();
  }

  loadArtists() {
    this.artistsService.getArtists().subscribe({
      next: (res) => (this.availableArtists = res.data),
      error: (err) => this.triggerSnackbar('Failed to load artists: ' + err.message, false)
    });
  }

  loadGenres() {
    this.genresService.getGenres().subscribe({
      next: (res) => (this.availableGenres = res.data.map((g: Genre) => g.name)),
      error: (err) => this.triggerSnackbar('Failed to load genres: ' + err.message, false)
    });
  }

  get titleValid(): boolean {
    return !!this.newAlbum.title && this.newAlbum.title.trim().length >= 2;
  }
  get dateValid(): boolean {
    return !!this.newAlbum.releaseDate;
  }
  get genresValid(): boolean {
    return this.newAlbum.genres.length > 0;
  }
  get formValid(): boolean {
    return this.titleValid && this.dateValid && this.genresValid;
  }

  toggleArtist(id: string) {
    const index = this.selectedArtistIds.indexOf(id);
    if (index > -1) this.selectedArtistIds.splice(index, 1);
    else this.selectedArtistIds.push(id);
  }

  toggleGenre(genre: string) {
    const index = this.newAlbum.genres.indexOf(genre);
    if (index > -1) this.newAlbum.genres.splice(index, 1);
    else this.newAlbum.genres.push(genre);
    this.touched.genres = true;
  }

  toggleArtistDropdown() { this.artistDropdownOpen = !this.artistDropdownOpen; }
  toggleGenreDropdown() { this.genreDropdownOpen = !this.genreDropdownOpen; }

  getSelectedArtists() {
    return this.availableArtists
      .filter((a) => this.selectedArtistIds.includes(a.id))
      .map((a) => a.name)
      .join(', ');
  }

  createAlbum() {
    this.touched.title = true;
    this.touched.releaseDate = true;
    this.touched.genres = true;

    if (!this.formValid) {
      this.triggerSnackbar('Please fill all required fields.', false);
      return;
    }

    const payload = {
      title: this.newAlbum.title.trim().replace(/\s+/g, ' '),
      releaseDate: this.newAlbum.releaseDate,
      genres: [...this.newAlbum.genres],
      artistIds: [...this.selectedArtistIds]
    };

    this.albumsService.createAlbum(payload).subscribe({
      next: (res) => {
        this.triggerSnackbar('Album created successfully!', true);

        setTimeout(() => {
          if (this.createFullAlbum)
            this.router.navigate(['/music-upload'], { queryParams: { albumTitle: payload.title } });
          else
            this.router.navigate(['/discover']);
        }, 1500);

        this.newAlbum = { id: '', title: '', releaseDate: '', genres: [] };
        this.selectedArtistIds = [];
        this.touched = { title: false, releaseDate: false, genres: false };
      },
      error: (err) => {
        this.triggerSnackbar('Error creating album: ' + err.message, false);
      }
    });
  }

  private triggerSnackbar(message: string, success: boolean) {
    this.snackbarMessage = message;
    this.showSnackbar = true;
    const snackbar = document.querySelector('.snackbar') as HTMLElement;
    if (snackbar) snackbar.style.backgroundColor = success ? '#1f27cf' : '#b00020';
    setTimeout(() => (this.showSnackbar = false), 3000);
  }
}
