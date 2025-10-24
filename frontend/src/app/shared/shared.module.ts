import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import { NavbarComponent } from './navbar/navbar.component';
import { ConfirmDialogComponent } from './confirm-dialog/confirm-dialog.component';
import { ContentEditDialogComponent } from './edit-dialog/edit-dialog.component';
import { MaterialModule } from "../material/material.module";
import { MatProgressSpinner } from "@angular/material/progress-spinner";
import { AlbumEditDialogComponent } from './album-edit-dialog/album-edit-dialog.component';
import { ArtistEditDialogComponent } from './artist-edit-dialog/artist-edit-dialog.component';

@NgModule({
  declarations: [
    NavbarComponent,
    ConfirmDialogComponent,
    ContentEditDialogComponent,
    AlbumEditDialogComponent,
    ArtistEditDialogComponent,
  ],
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MaterialModule,
    MatProgressSpinner
  ],
  exports: [
    NavbarComponent,
    ConfirmDialogComponent,
    ContentEditDialogComponent,
  ]
})
export class SharedModule { }
