import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ArtistCreationComponent } from './artist-creation/artist-creation.component';

const routes: Routes = [
  { path: '', component: ArtistCreationComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule { }
