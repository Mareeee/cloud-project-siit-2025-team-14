import { Component } from '@angular/core';
import { SongsService } from '../song.service';
import { Song } from '../music.model';

@Component({
  selector: 'app-upload-music',
  templateUrl: './upload-music.component.html',
  styleUrl: './upload-music.component.css',
})
export class UploadMusicComponent {
  constructor(private songsService: SongsService) {}

  response = 'The response will show up here';

  genres: string[] = ['Pop', 'Rock', 'Hip-Hop'];
  authors: string[] = ['Aca Lukas', 'Darko Lazić', 'Viki Miljković'];
  albums: string[] = ['Godinu Dana 300 kafana', 'Istina je da te lažem', 'Loša sreća'];

  newSong: Song = {
    title: '',
    authorId: "",
    genres: [],
    authors: [],
    album: []
  };

  selectedCover!: File;
  coverPreview: string | ArrayBuffer | null = null;

  selectedAudio!: File;
  audioPreview: string | null = null;

  onCoverSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.selectedCover = file;

      const reader = new FileReader();
      reader.onload = e => this.coverPreview = reader.result;
      reader.readAsDataURL(file);
    }
  }

  removeCover() {
    this.selectedCover = null!;
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
    this.selectedAudio = null!;
    this.audioPreview = null;
  }

  addSong() {
    if (!this.newSong.title || !this.selectedAudio) {
      this.response = 'Please provide required fields (title and audio).';
      return;
    }

    this.songsService
      .addSong(this.newSong, this.selectedCover, this.selectedAudio)
      .subscribe({
        next: (res) => (this.response = 'Success: ' + JSON.stringify(res)),
        error: (err) => (this.response = 'Error: ' + JSON.stringify(err)),
      });
  }
}
