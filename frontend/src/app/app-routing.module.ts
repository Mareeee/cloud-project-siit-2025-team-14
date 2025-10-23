import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ContentOverviewComponent } from './content-overview/content-overview.component';
import { ArtistCreationComponent } from './artist-creation/artist-creation.component';
import { UploadMusicComponent } from './upload-music/upload-music.component';
import { LoginComponent } from './auth/login/login.component';
import { RegistrationComponent } from './auth/registration/registration.component';
import { DiscoverComponent } from './discover/discover.component';
import { AlbumsCreationComponent } from './albums-creation/albums-creation.component';
import { ManageContentComponent } from './admin/manage-content/manage-content.component';
import { AuthGuard } from './auth/auth.guard';
import { SubscriptionsComponent } from './subscriptions/subscriptions.component';
import { FeedPageComponent } from './feed/feed/feed.component';
import { RedirectComponent } from './redirect/redirect.component';

const routes: Routes = [
  { path: '', component: RedirectComponent },
  { path: 'feed', component: FeedPageComponent, canActivate: [AuthGuard], data: { role: 'User' } },
  { path: 'content-overview', component: ContentOverviewComponent, canActivate: [AuthGuard], data: { role: 'User' } },
  { path: 'admin/manage-content', component: ManageContentComponent, canActivate: [AuthGuard], data: { role: 'Admin' } },
  { path: 'register', component: RegistrationComponent },
  { path: 'artist-create', component: ArtistCreationComponent, canActivate: [AuthGuard], data: { role: 'Admin' } },
  { path: 'subscriptions', component: SubscriptionsComponent, canActivate: [AuthGuard], data: { role: 'User' } },
  { path: 'login', component: LoginComponent },
  { path: 'album-create', component: AlbumsCreationComponent, canActivate: [AuthGuard], data: { role: 'Admin' } },
  { path: 'music-upload', component: UploadMusicComponent, canActivate: [AuthGuard], data: { role: 'Admin' } },
  { path: 'discover', component: DiscoverComponent, canActivate: [AuthGuard], data: { role: 'User' } },
  { path: '**', redirectTo: '' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule { }
