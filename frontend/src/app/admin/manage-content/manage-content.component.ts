import { Component } from '@angular/core';
import { forkJoin } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';

import { Song } from '../../models/song.model';
import { Artist } from '../../models/artist.model';
import { Album } from '../../models/album.model';

import { SongsService } from '../../services/song.service';
import { ArtistsService } from '../../services/artist.service';
import { AlbumsService } from '../../services/albums.service';
import { GenresService } from '../../services/genres.service';

import { ConfirmDialogComponent, ConfirmDialogData } from '../../shared/confirm-dialog/confirm-dialog.component';
import { ContentEditDialogComponent } from '../../shared/edit-dialog/edit-dialog.component';
import { AlbumEditDialogComponent, AlbumEditResult } from '../../shared/album-edit-dialog/album-edit-dialog.component';
import { ArtistEditDialogComponent, ArtistEditResult } from '../../shared/artist-edit-dialog/artist-edit-dialog.component';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-manage-content',
  templateUrl: './manage-content.component.html',
  styleUrls: ['./manage-content.component.css']
})
export class ManageContentComponent {
  songs: Song[] = [];
  artists: Artist[] = [];
  loading = true;
  albums: Album[] = [];
  albumsLoading = true;
  allGenres: string[] = [];

  constructor(
    private songsService: SongsService,
    private artistsService: ArtistsService,
    private albumsService: AlbumsService,
    private genresService: GenresService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) {
    forkJoin({
      artists: this.artistsService.getArtists(),
      songs: this.songsService.getSongs(),
    }).subscribe(({ songs, artists }) => {
      this.artists = artists.data || [];

      this.songs = (songs.data || []).map((song: any) => {
        const linked = this.artists.filter(a => song.artistIds?.includes(a.id));
        return {
          ...song,
          artistNames: linked.map(a => a.name),
          artistBios: linked.map(a => a.biography),
          artistGenres: linked.flatMap(a => a.genres),
        };
      });

      this.loading = false;
    });

    this.albumsService.getAlbums().subscribe({
      next: (res) => { this.albums = res.data || []; this.albumsLoading = false; },
      error: () => { this.albums = []; this.albumsLoading = false; }
    });

    this.genresService.getGenres().subscribe({
      next: (res) => { this.allGenres = (res.data || []).map((g: any) => g.name); },
      error: () => { this.allGenres = []; }
    });
  }

  openEdit(song: Song) {
    const ref = this.dialog.open(ContentEditDialogComponent, {
      width: '760px',
      maxHeight: 'calc(100vh - 100px)',
      panelClass: ['plain-dialog', 'plain-dialog-pane'],
      backdropClass: 'dark-backdrop',
      data: { song }
    });

    ref.afterClosed().subscribe((res: any) => {
      if (!res) return;

      this.songsService.editSong(res.patch, res.newCoverFile, res.newAudioFile).subscribe({
        next: (data) => {
          this.snackBar.open(`Song ${res.patch.title} has been edited!`, 'Close', { duration: 3000 })

          if (res.patch) {
            const idx = this.songs.findIndex(s => s.id === song.id);
            if (idx > -1) this.songs[idx] = { ...this.songs[idx], ...res.patch };
          }

          if (res.newCoverFile) {
            const previewUrl = URL.createObjectURL(res.newCoverFile);
            const idx = this.songs.findIndex(s => s.id === song.id);
            if (idx > -1) this.songs[idx] = { ...this.songs[idx], imageUrl: previewUrl };
          }
        },
        error: (err) => {
          console.error(err);
          this.snackBar.open('Failed to edit song.', 'Close', { duration: 3000 })
        }
      });
    });
  }

  confirmDelete(song: Song) {
    const data: ConfirmDialogData = {
      title: 'Delete content',
      message: `Are you sure you want to delete “${song.title}”?`,
      confirmText: 'Delete',
      cancelText: 'Cancel'
    };

    const ref = this.dialog.open(ConfirmDialogComponent, {
      width: '570px',
      maxHeight: 'calc(100vh - 96px)',
      panelClass: ['plain-dialog', 'plain-dialog-pane'],
      backdropClass: 'dark-backdrop',
      data
    });

    ref.afterClosed().subscribe((ok: boolean) => {
      if (!ok) return;

      this.songsService.deleteSong(song.id).subscribe({
        next: () => {
          this.songs = this.songs.filter(s => s.id !== song.id);
          this.snackBar.open('Song deleted', 'Close', { duration: 2000 });
        },
        error: (err) => {
          console.error(err);
          this.snackBar.open('Delete failed. Please try again.', 'Close', { duration: 3000 });
        }
      });
    });
  }

  authorLine(song: Song) {
    return (song.artistNames && song.artistNames.length)
      ? song.artistNames.join(', ')
      : 'Unknown artist';
  }

  openAlbumEdit(album: Album) {
    const ref = this.dialog.open(AlbumEditDialogComponent, {
      width: '640px',
      maxHeight: 'calc(100vh - 96px)',
      panelClass: ['plain-dialog', 'plain-dialog-pane'],
      backdropClass: 'dark-backdrop',
      data: { album, allGenres: this.allGenres }
    });

    ref.afterClosed().subscribe((res: AlbumEditResult | null) => {
      if (!res?.patch) return;
      const idx = this.albums.findIndex(a => a.id === album.id);
      if (idx > -1) this.albums[idx] = { ...this.albums[idx], ...res.patch };
    });
  }

  confirmAlbumDelete(album: Album) {
    const data: ConfirmDialogData = {
      title: 'Delete album',
      message: `Are you sure you want to delete “${album.title}”?
Note: Deleting an album will also delete its songs.`,
      confirmText: 'Delete',
      cancelText: 'Cancel'
    };

    const ref = this.dialog.open(ConfirmDialogComponent, {
      width: '600px',
      maxHeight: 'calc(100vh - 96px)',
      panelClass: ['plain-dialog', 'plain-dialog-pane'],
      backdropClass: 'dark-backdrop',
      data
    });

    ref.afterClosed().subscribe((ok: boolean) => {
      if (!ok) return;
      this.albums = this.albums.filter(a => a.id !== album.id);
    });
  }

  openArtistEdit(artist: Artist) {
    const ref = this.dialog.open(ArtistEditDialogComponent, {
      width: '640px',
      maxHeight: 'calc(100vh - 96px)',
      panelClass: ['plain-dialog', 'plain-dialog-pane'],
      backdropClass: 'dark-backdrop',
      data: { artist }
    });

    ref.afterClosed().subscribe((res: ArtistEditResult | null) => {
      if (!res?.patch) return;
      const idx = this.artists.findIndex(a => a.id === artist.id);
      if (idx > -1) this.artists[idx] = { ...this.artists[idx], ...res.patch };
    });
  }

  confirmArtistDelete(artist: Artist) {
    const data: ConfirmDialogData = {
      title: 'Delete artist',
      message: `Are you sure you want to delete “${artist.name}”?
Note: Deleting an artist does not delete songs.`,
      confirmText: 'Delete',
      cancelText: 'Cancel'
    };

    const ref = this.dialog.open(ConfirmDialogComponent, {
      width: '650px',
      maxHeight: 'calc(100vh - 96px)',
      panelClass: ['plain-dialog', 'plain-dialog-pane'],
      backdropClass: 'dark-backdrop',
      data
    });

    ref.afterClosed().subscribe((ok: boolean) => {
      if (!ok) return;
      this.artists = this.artists.filter(a => a.id !== artist.id);
    });
  }
}
