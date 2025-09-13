import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ContentOverviewComponent } from './content-overview/content-overview.component';
import { HomeComponent } from './home/home.component';
import { ArtistCreationComponent } from './artist-creation/artist-creation.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'content-overview', component: ContentOverviewComponent },
  { path: 'artist-create', component: ArtistCreationComponent },
  { path: '**', redirectTo: '' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule { }
