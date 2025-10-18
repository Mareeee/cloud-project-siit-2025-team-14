import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ContentOverviewComponent } from './content-overview/content-overview.component';
import { HomeComponent } from './home/home.component';
import { ArtistCreationComponent } from './artist-creation/artist-creation.component';
import { UploadMusicComponent } from './upload-music/upload-music.component';
import { DiscoverComponent } from './discover/discover.component';
import { AlbumsCreationComponent } from './albums-creation/albums-creation.component';

const routes: Routes = [
  { path: '', component: AlbumsCreationComponent },
  { path: 'content-overview', component: ContentOverviewComponent },
  { path: 'artist-create', component: ArtistCreationComponent },
  { path: 'music-upload', component: UploadMusicComponent },
  { path: 'discover', component: DiscoverComponent },
  { path: '**', redirectTo: '' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule { }
