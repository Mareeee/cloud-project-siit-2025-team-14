import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { SongsService } from '../services/song.service';
import { ArtistsService } from '../services/artist.service';
import { AlbumsService } from '../services/albums.service';
import { GenresService } from '../services/genres.service';
import { Song } from '../models/song.model';
import { Router, ActivatedRoute } from '@angular/router';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Artist } from '../models/artist.model';
import { Album } from '../models/album.model';
import { Genre } from '../models/genre.model';

@Component({
  selector: 'app-upload-music',
  templateUrl: './upload-music.component.html',
  styleUrls: ['./upload-music.component.css']
})
export class UploadMusicComponent implements OnInit {
  genres: string[] = [];
  artists: Artist[] = [];
  albums: Album[] = [];

  submitted = false;
  isUploading = false;

  selectedCover!: File | null;
  coverPreview: string | ArrayBuffer | null = null;

  selectedAudio!: File | null;
  audioPreview: string | null = null;

  uploadMusicForm: FormGroup;

  constructor(
    private songsService: SongsService,
    private artistsService: ArtistsService,
    private albumsService: AlbumsService,
    private genresService: GenresService,
    private snackBar: MatSnackBar,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.uploadMusicForm = new FormGroup({
      title: new FormControl('', [Validators.required]),
      genres: new FormControl([], [Validators.required]),
      artistIds: new FormControl([], [Validators.required]),
      albumId: new FormControl(''),
      isFullAlbum: new FormControl(false)
    });
  }

  ngOnInit() {
    this.loadArtists();
    this.loadAlbums();
    this.loadGenres();
  }

  loadArtists() {
    this.artistsService.getArtists().subscribe({
      next: (res) => (this.artists = res.data),
      error: () =>
        this.snackBar.open('Failed to load artists', 'Close', { duration: 3000 })
    });
  }

  loadAlbums() {
    this.albumsService.getAlbums().subscribe({
      next: (res) => {
        this.albums = res.data;
        this.checkAlbumFromUrl();
      },
      error: () =>
        this.snackBar.open('Failed to load albums', 'Close', { duration: 3000 })
    });
  }

  loadGenres() {
    this.genresService.getGenres().subscribe({
      next: (res) => (this.genres = res.data.map((g: Genre) => g.name)),
      error: () =>
        this.snackBar.open('Failed to load genres', 'Close', { duration: 3000 })
    });
  }

  checkAlbumFromUrl() {
    const albumTitle = this.route.snapshot.queryParamMap.get('albumTitle');
    if (albumTitle) {
      const targetAlbum = this.albums.find(a => a.title === albumTitle);
      if (targetAlbum) {
        this.uploadMusicForm.patchValue({
          albumId: targetAlbum.id,
          isFullAlbum: true
        });
      }
    }
  }

  onCoverSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.selectedCover = file;
      const reader = new FileReader();
      reader.onload = () => (this.coverPreview = reader.result);
      reader.readAsDataURL(file);
    }
  }

  removeCover() {
    this.selectedCover = null;
    this.coverPreview = null;
  }

  onAudioSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.selectedAudio = file;
      this.audioPreview = URL.createObjectURL(file);
    }
  }

  removeAudio() {
    this.selectedAudio = null;
    this.audioPreview = null;
  }

  addSong() {
    this.submitted = true;

    if (!this.uploadMusicForm.valid || !this.selectedCover || !this.selectedAudio) {
      this.uploadMusicForm.markAllAsTouched();
      this.snackBar.open('Please fill all required fields', 'Close', { duration: 3000 });
      return;
    }

    const formValue = this.uploadMusicForm.value;
    const newSong: Song = {
      id: '',
      title: formValue.title,
      genres: formValue.genres,
      artistIds: formValue.artistIds,
      albumId: formValue.albumId,
      creationDate: ''
    };

    console.log(newSong)

    this.isUploading = true;

    this.songsService.addSong(newSong, this.selectedCover, this.selectedAudio).subscribe({
      next: () => {
        this.isUploading = false;
        const isFullAlbum = formValue.isFullAlbum;
        const currentAlbumId = formValue.albumId;

        if (isFullAlbum) {
          this.snackBar.open('Song added to album. You can now add another!', 'Close', { duration: 3000 });

          this.uploadMusicForm.reset({
            isFullAlbum: true,
            albumId: currentAlbumId
          });

          this.selectedCover = null;
          this.coverPreview = null;
          this.selectedAudio = null;
          this.audioPreview = null;
          this.submitted = false;
        } else {
          this.snackBar.open('Song uploaded successfully!', 'Close', { duration: 3000 });
          this.router.navigate(['/discover']);
        }
      },
      error: () => {
        this.isUploading = false;
        this.snackBar.open('Failed to upload song.', 'Close', { duration: 3000 });
      }
    });
  }
}
