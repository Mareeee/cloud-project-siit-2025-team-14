import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ArtistCreationComponent } from './artist-creation/artist-creation.component';
import { provideHttpClient, withFetch, withInterceptorsFromDi } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from './material/material.module';
import { UploadMusicComponent } from './upload-music/upload-music.component';
import { HomeComponent } from './home/home.component';
import { ContentOverviewComponent } from './content-overview/content-overview.component';
import { SharedModule } from './shared/shared.module';

@NgModule({
  declarations: [
    AppComponent,
    UploadMusicComponent,
    ContentOverviewComponent,
    ArtistCreationComponent,
    HomeComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    MaterialModule,
    AppRoutingModule,
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
