import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, Validators, FormGroup, FormControl } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ArtistsService } from '../../services/artist.service';
import { AlbumsService } from '../../services/albums.service';
import { GenresService } from '../../services/genres.service';
import { Artist } from '../../models/artist.model';
import { Album } from '../../models/album.model';
import { Genre } from '../../models/genre.model';
import { Song } from '../../models/song.model';

export interface ContentEditData {
  song: Song;
}

export interface EditDialogResult {
  patch: Partial<Song>;
  newCoverFile?: File | null;
  newAudioFile?: File | null;
}

@Component({
  selector: 'app-content-edit-dialog',
  templateUrl: './edit-dialog.component.html',
  styleUrls: ['./edit-dialog.component.css']
})
export class ContentEditDialogComponent implements OnInit {
  form!: FormGroup;

  genres: string[] = [];
  artists: Artist[] = [];
  albums: Album[] = [];

  selectedCover: File | null = null;
  coverPreview: string | ArrayBuffer | null = null;

  selectedAudio: File | null = null;
  audioPreview: string | null = null;

  submitted = false;
  isUploading = false;

  constructor(
    private fb: FormBuilder,
    private artistsService: ArtistsService,
    private albumsService: AlbumsService,
    private genresService: GenresService,
    public ref: MatDialogRef<ContentEditDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ContentEditData
  ) {
    this.form = this.fb.group({
      title: new FormControl('', [Validators.required]),
      genres: new FormControl<string[]>([], [Validators.required]),
      artistIds: new FormControl<string[]>([], [Validators.required]),
      albumId: new FormControl(''),
      isFullAlbum: new FormControl(false)
    });

    const s = data.song;
    this.form.patchValue({
      title: s.title ?? '',
      genres: (s.genres ?? []) as string[],
      artistIds: (s.artistIds ?? []) as string[],
      albumId: s.albumId ?? '',
      isFullAlbum: false
    });

    if (s.imageUrl) this.coverPreview = s.imageUrl;
  }

  ngOnInit(): void {
    this.artistsService.getArtists().subscribe({ next: res => (this.artists = res.data) });
    this.albumsService.getAlbums().subscribe({ next: res => (this.albums = res.data) });
    this.genresService.getGenres().subscribe({ next: res => (this.genres = res.data.map((g: Genre) => g.name)) });
  }

  onCoverSelected(event: any) {
    const file = event?.target?.files?.[0];
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
    const file = event?.target?.files?.[0];
    if (file) {
      this.selectedAudio = file;
      this.audioPreview = URL.createObjectURL(file);
    }
  }
  removeAudio() {
    this.selectedAudio = null;
    this.audioPreview = null;
  }

  cancel() { this.ref.close(null); }

  save() {
    this.submitted = true;

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const v = this.form.getRawValue() as {
      title: string;
      genres: string[];
      artistIds: string[];
      albumId?: string | null;
      isFullAlbum?: boolean;
    };

    const patch: Partial<Song> = {
      title: v.title,
      genres: v.genres || [],
      artistIds: v.artistIds || [],
      albumId: v.albumId || ''
    };

    const result: EditDialogResult = {
      patch,
      newCoverFile: this.selectedCover,
      newAudioFile: this.selectedAudio
    };

    this.ref.close(result);
  }
}
