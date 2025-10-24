import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, Validators, FormGroup, FormControl } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

import { GenresService } from '../../services/genres.service';
import { Genre } from '../../models/genre.model';
import { Artist } from '../../models/artist.model';

export interface ArtistEditData {
  artist: Artist;
}

export interface ArtistEditResult {
  patch: Partial<Artist>;
}

@Component({
  selector: 'app-artist-edit-dialog',
  templateUrl: './artist-edit-dialog.component.html',
  styleUrls: ['./artist-edit-dialog.component.css']
})
export class ArtistEditDialogComponent implements OnInit {
  form!: FormGroup;

  genres: Genre[] = [];
  genreNameById: Record<string, string> = {};

  constructor(
    private fb: FormBuilder,
    private genresService: GenresService,
    public ref: MatDialogRef<ArtistEditDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ArtistEditData
  ) {
    const a = data.artist;

    this.form = this.fb.group({
      name: new FormControl<string>({ value: a.name ?? '', disabled: true }, {
        nonNullable: true,
        validators: [Validators.required, Validators.maxLength(160)],
      }),
      biography: new FormControl<string>(a.biography ?? '', {
        nonNullable: true,
        validators: [Validators.maxLength(5000)],
      }),
      genreIds: new FormControl<string[]>(Array.isArray((a as any).genreIds) ? (a as any).genreIds : [], {
        nonNullable: true,
        validators: [Validators.required],
      }),
    });
  }

  ngOnInit(): void {
    this.genresService.getGenres().subscribe({
      next: (res) => {
        this.genres = res.data || [];
        this.genreNameById = Object.fromEntries(this.genres.map((g: Genre) => [g.id, g.name]));
      },
      error: () => {
        this.genres = [];
        this.genreNameById = {};
      },
    });
  }

  cancel(): void {
    this.ref.close(null);
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const v = this.form.getRawValue() as {
      name: string;
      biography: string;
      genreIds: string[];
    };

    const patch: Partial<Artist> = {
      id: this.data.artist.id,
      name: this.data.artist.name,
      biography: v.biography || '',
      genreIds: v.genreIds || [],
    };

    const result: ArtistEditResult = { patch };
    this.ref.close(result);
  }
}
