import { Component } from '@angular/core';
import { SongsService } from '../song.service';
import { ArtistsService } from '../artist.service';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-content-overview',
  templateUrl: './content-overview.component.html',
  styleUrls: ['./content-overview.component.css']
})
export class ContentOverviewComponent {
  songs: any[] = [];
  artists: any[] = [];

  constructor(
    private songsService: SongsService,
    private artistsService: ArtistsService,
  ) {
    forkJoin({
      songs: this.songsService.getSongs(),
      artists: this.artistsService.getArtists()
    }).subscribe(({ songs, artists }) => {
      this.artists = artists.data || [];

      this.songs = (songs.data || []).map((song: any) => {
        const artist = this.artists.find(a => a.id === song.artistId);
        return {
          ...song,
          artistName: artist ? artist.name : 'Unknown Artist',
          artistBio: artist ? artist.biography : '',
          artistGenres: artist ? artist.genres : []
        };
      });
    });

  }
}
