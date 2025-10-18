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
  genres: string[] = [];

  constructor(
    private fb: FormBuilder,
    private genresService: GenresService,
    public ref: MatDialogRef<ArtistEditDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ArtistEditData
  ) {
    this.form = this.fb.group({
      name: new FormControl('', [Validators.required, Validators.maxLength(160)]),
      biography: new FormControl('', [Validators.maxLength(5000)]),
      genres: new FormControl<string[]>([], [Validators.required]),
    });

    const a = data.artist;
    this.form.patchValue({
      name: a.name ?? '',
      biography: a.biography ?? '',
      genres: (a.genres ?? []) as string[],
    });
  }

  ngOnInit(): void {
    this.genresService.getGenres().subscribe({
      next: (res) => (this.genres = (res.data || []).map((g: Genre) => g.name)),
      error: () => (this.genres = []),
    });
  }

  cancel() { this.ref.close(null); }

  save() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const v = this.form.getRawValue() as {
      name: string;
      biography: string;
      genres: string[];
    };

    const patch: Partial<Artist> = {
      name: v.name,
      biography: v.biography || '',
      genres: v.genres || [],
    };

    const result: ArtistEditResult = { patch };
    this.ref.close(result);
  }
}
