import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-lyrics',
  templateUrl: './lyrics.component.html',
  styleUrls: ['./lyrics.component.css']
})
export class LyricsComponent {
  constructor(
    public dialogRef: MatDialogRef<LyricsComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { title: string; lyrics: string }
  ) { }

  close() {
    this.dialogRef.close();
  }
}
