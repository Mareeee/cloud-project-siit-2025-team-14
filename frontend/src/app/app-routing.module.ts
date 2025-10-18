import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ContentOverviewComponent } from './content-overview/content-overview.component';
import { ArtistCreationComponent } from './artist-creation/artist-creation.component';
import { UploadMusicComponent } from './upload-music/upload-music.component';
import { LoginComponent } from './auth/login/login.component';
import { RegistrationComponent } from './auth/registration/registration.component';
import { DiscoverComponent } from './discover/discover.component';
import { AlbumsCreationComponent } from './albums-creation/albums-creation.component';
import { AuthGuard } from './auth/auth.guard';

const routes: Routes = [
  { path: '', component: DiscoverComponent },
  { path: 'content-overview', component: ContentOverviewComponent },
  { path: 'artist-create', component: ArtistCreationComponent, canActivate: [AuthGuard], data: { role: 'Admin' }},
  { path: 'music-upload', component: UploadMusicComponent},
  { path: 'login', component: LoginComponent},
  { path: 'register', component: RegistrationComponent},
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
