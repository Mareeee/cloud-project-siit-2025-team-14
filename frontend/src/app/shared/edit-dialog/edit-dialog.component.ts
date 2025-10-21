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
  s: Song | undefined;

  genres: Genre[] = [];
  genreNameById: Record<string, string> = {};
  artists: Artist[] = [];
  albums: Album[] = [];

  selectedCover: File | null = null;
  coverPreview: string | null = null;

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
      title: new FormControl<string>('', { nonNullable: true, validators: [Validators.required] }),
      genreIds: new FormControl<string[]>([], { nonNullable: true, validators: [Validators.required] }),
      artistIds: new FormControl<string[]>([], { nonNullable: true, validators: [Validators.required] }),
      albumId: new FormControl<string>('', { nonNullable: true }),
      coverPreview: new FormControl<string>('', { nonNullable: true, validators: [Validators.required] }),
      audioPreview: new FormControl<string>('', { nonNullable: true, validators: [Validators.required] }),
    });

    this.s = data.song;

    this.form.patchValue({
      title: this.s.title ?? '',
      genreIds: (this.s.genreIds ?? []) as string[],
      artistIds: (this.s.artistIds ?? []) as string[],
      albumId: this.s.albumId ?? '',
    });

    if (this.s.imageUrl) {
      this.coverPreview = this.s.imageUrl;
      this.form.get('coverPreview')?.setValue(this.s.imageUrl);
    }
    if (this.s.audioUrl) {
      this.audioPreview = this.s.audioUrl;
      this.form.get('audioPreview')?.setValue(this.s.audioUrl);
    }
  }

  ngOnInit(): void {
    this.artistsService.getArtists().subscribe({ next: res => (this.artists = res.data || []) });
    this.albumsService.getAlbums().subscribe({ next: res => (this.albums = res.data || []) });
    this.genresService.getGenres().subscribe({
      next: res => {
        this.genres = res.data || [];
        this.genreNameById = Object.fromEntries(this.genres.map((g: Genre) => [g.id, g.name]));
      }
    });
  }

  onCoverSelected(event: Event) {
    const input = event.target as HTMLInputElement | null;
    const file = input?.files && input.files[0];
    if (!file) return;

    this.selectedCover = file;

    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        this.coverPreview = reader.result;
        this.form.get('coverPreview')?.setValue(reader.result);
        this.form.get('coverPreview')?.markAsDirty();
      }
    };
    reader.readAsDataURL(file);

    if (input) input.value = '';
  }

  removeCover() {
    this.selectedCover = null;
    this.coverPreview = null;
    this.form.get('coverPreview')?.setValue('');
    this.form.get('coverPreview')?.markAsTouched();
  }

  onAudioSelected(event: Event) {
    const input = event.target as HTMLInputElement | null;
    const file = input?.files && input.files[0];
    if (!file) return;

    if (this.audioPreview && this.audioPreview.startsWith('blob:')) {
      try { URL.revokeObjectURL(this.audioPreview); } catch { }
    }

    this.selectedAudio = file;
    const url = URL.createObjectURL(file);
    this.audioPreview = url;
    this.form.get('audioPreview')?.setValue(url);
    this.form.get('audioPreview')?.markAsDirty();

    if (input) input.value = '';
  }

  removeAudio() {
    this.selectedAudio = null;
    if (this.audioPreview && this.audioPreview.startsWith('blob:')) {
      try { URL.revokeObjectURL(this.audioPreview); } catch { }
    }
    this.audioPreview = null;
    this.form.get('audioPreview')?.setValue('');
    this.form.get('audioPreview')?.markAsTouched();
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
      genreIds: string[];
      artistIds: string[];
      albumId?: string | null;
    };

    const patch: Partial<Song> = {
      id: this.s?.id,
      title: v.title,
      genreIds: v.genreIds || [],
      artistIds: v.artistIds || [],
      albumId: v.albumId || ''
    };

    if (this.coverPreview) patch.imageUrl = this.coverPreview;
    if (this.audioPreview) patch.audioUrl = this.audioPreview;

    const result: EditDialogResult = {
      patch,
      newCoverFile: this.selectedCover ?? null,
      newAudioFile: this.selectedAudio ?? null,
    };

    this.ref.close(result);
  }
}
