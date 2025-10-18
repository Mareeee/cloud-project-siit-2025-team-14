import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ArtistCreationComponent } from './artist-creation/artist-creation.component';
import { provideHttpClient, withFetch, withInterceptorsFromDi } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { FormsModule } from '@angular/forms';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MaterialModule } from './material/material.module';
import { UploadMusicComponent } from './upload-music/upload-music.component';
import { HomeComponent } from './home/home.component';
import { ContentOverviewComponent } from './content-overview/content-overview.component';
import { DiscoverComponent } from './discover/discover.component';
import { AlbumsCreationComponent } from './albums-creation/albums-creation.component';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCardModule } from '@angular/material/card';
import { SharedModule } from './shared/shared.module';

@NgModule({
  declarations: [
    AppComponent,
    UploadMusicComponent,
    ContentOverviewComponent,
    ArtistCreationComponent,
    HomeComponent,
    DiscoverComponent,
    AlbumsCreationComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    MaterialModule,
    AppRoutingModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
    MatCardModule,
    SharedModule,
  ],
  providers: [
    provideClientHydration(),
    provideAnimationsAsync(),
    provideHttpClient(withFetch(), withInterceptorsFromDi())
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
