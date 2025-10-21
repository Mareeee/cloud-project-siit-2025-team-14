import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, Validators, FormGroup, FormControl } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { GenresService } from '../../services/genres.service';
import { ArtistsService } from '../../services/artist.service';
import { Album } from '../../models/album.model';
import { Artist } from '../../models/artist.model';

export interface AlbumEditData {
  album: Album;
}

export interface AlbumEditResult {
  patch: Partial<Album>;
}

@Component({
  selector: 'app-album-edit-dialog',
  templateUrl: './album-edit-dialog.component.html',
  styleUrls: ['./album-edit-dialog.component.css']
})
export class AlbumEditDialogComponent implements OnInit {
  form!: FormGroup;
  genres: string[] = [];
  artists: Artist[] = [];

  constructor(
    private fb: FormBuilder,
    private genresService: GenresService,
    private artistsService: ArtistsService,
    public ref: MatDialogRef<AlbumEditDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: AlbumEditData
  ) {
    this.form = this.fb.group({
      title: new FormControl('', [Validators.required]),
      releaseDate: new FormControl('', [Validators.required]),
      genres: new FormControl<string[]>([], [Validators.required]),
      artistIds: new FormControl<string[]>([])
    });

    const a = data.album;
    this.form.patchValue({
      title: a.title ?? '',
      releaseDate: a.releaseDate ?? '',
      genres: (a.genres ?? []) as string[],
      artistIds: (a.artistIds ?? []) as string[],
    });
  }

  ngOnInit(): void {
    this.genresService.getGenres().subscribe({
      next: (res) => (this.genres = (res.data || []).map((g: any) => g.name)),
      error: () => (this.genres = []),
    });

    this.artistsService.getArtists().subscribe({
      next: (res) => (this.artists = res.data || []),
      error: () => (this.artists = []),
    });
  }

  cancel() {
    this.ref.close(null);
  }

  save() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const v = this.form.getRawValue() as {
      title: string;
      releaseDate: string;
      genres: string[];
      artistIds: string[];
    };

    const patch: Partial<Album> = {
      title: v.title,
      releaseDate: v.releaseDate,
      genres: v.genres || [],
      artistIds: v.artistIds || [],
    };

    const result: AlbumEditResult = { patch };
    this.ref.close(result);
  }
}
