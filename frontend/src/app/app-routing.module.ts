import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ContentOverviewComponent } from './content-overview/content-overview.component';
import { HomeComponent } from './home/home.component';
import { ArtistCreationComponent } from './artist-creation/artist-creation.component';
import { UploadMusicComponent } from './upload-music/upload-music.component';
import { LoginComponent } from './auth/login/login.component';
import { RegistrationComponent } from './auth/registration/registration.component';
import { DiscoverComponent } from './discover/discover.component';
import { AlbumsCreationComponent } from './albums-creation/albums-creation.component';
import { ManageContentComponent } from './admin/manage-content/manage-content.component';

const routes: Routes = [
  { path: '', component: DiscoverComponent },
  { path: 'content-overview', component: ContentOverviewComponent },
  { path: 'admin/manage-content', component: ManageContentComponent },
  { path: 'artist-create', component: ArtistCreationComponent },
  { path: 'music-upload', component: UploadMusicComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegistrationComponent },
  { path: 'album-create', component: AlbumsCreationComponent },
  { path: 'music-upload', component: UploadMusicComponent },
  { path: 'discover', component: DiscoverComponent },
  { path: '**', redirectTo: '' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule { }
