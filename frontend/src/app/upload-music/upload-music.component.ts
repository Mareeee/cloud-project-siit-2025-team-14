import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { SongsService } from '../services/song.service';
import { ArtistsService } from '../services/artist.service';
import { Song } from '../models/song.model';
import { AVAILABLE_GENRES } from '../utils/genres';
import { Router } from '@angular/router';
import { FormControl, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-upload-music',
  templateUrl: './upload-music.component.html',
  styleUrl: './upload-music.component.css',
})
export class UploadMusicComponent implements OnInit {
  genres = AVAILABLE_GENRES;
  artists: any[] = [];
  albums: string[] = [
    'Godinu Dana 300 kafana',
    'Istina je da te lažem',
    'Loša sreća',
    'Poziv',
  ];
  submitted = false;

  selectedCover!: File | null;
  coverPreview: string | ArrayBuffer | null = null;

  selectedAudio!: File | null;
  audioPreview: string | null = null;

  uploadMusicForm: FormGroup;

  constructor(
    private songsService: SongsService,
    private artistsService: ArtistsService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {
    this.uploadMusicForm = new FormGroup({
      title: new FormControl('', [Validators.required]),
      genres: new FormControl([], [Validators.required]),
      artistIds: new FormControl([], [Validators.required]),
      albumId: new FormControl(''),
    });
  }

  ngOnInit() {
    this.loadArtists();
  }

  loadArtists() {
    this.artistsService.getArtists().subscribe({
      next: (res) => {
        this.artists = res.data.map((a: any) => ({ id: a.id, name: a.name }));
      },
      error: () => {
        this.snackBar.open('Failed to load artists', 'Close', {
          duration: 3000,
        });
      },
    });
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

    if (
      !this.uploadMusicForm.valid ||
      !this.selectedCover ||
      !this.selectedAudio
    ) {
      this.uploadMusicForm.markAllAsTouched();
      this.snackBar.open('Please fill all required fields', 'Close', {
        duration: 3000,
      });
      return;
    }

    const newSong: Song = {
      id: '',
      title: this.uploadMusicForm.value.title,
      genres: this.uploadMusicForm.value.genres,
      artistIds: this.uploadMusicForm.value.artistIds,
      albumId: this.uploadMusicForm.value.albumId,
      creationDate: '',
    };

    this.songsService
      .addSong(newSong, this.selectedCover, this.selectedAudio)
      .subscribe({
        next: () => {
          this.snackBar.open('Song uploaded successfully!', 'Close', {
            duration: 3000,
          });
          this.router.navigate(['/content-overview']);
        },
        error: () => {
          this.snackBar.open('Failed to upload song.', 'Close', {
            duration: 3000,
          });
        },
      });
  }
}
