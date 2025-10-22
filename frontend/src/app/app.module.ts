import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ArtistCreationComponent } from './artist-creation/artist-creation.component';
import { HTTP_INTERCEPTORS, provideHttpClient, withFetch, withInterceptorsFromDi } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from './material/material.module';
import { UploadMusicComponent } from './upload-music/upload-music.component';
import { HomeComponent } from './home/home.component';
import { ContentOverviewComponent } from './content-overview/content-overview.component';
import { AuthModule } from './auth/auth.module';
import { DiscoverComponent } from './discover/discover.component';
import { AlbumsCreationComponent } from './albums-creation/albums-creation.component';
import { AuthInterceptor } from './auth/auth.interceptor';
import { ManageContentComponent } from './admin/manage-content/manage-content.component';
import { SharedModule } from './shared/shared.module';
import { SubscriptionsComponent } from './subscriptions/subscriptions.component';
import { FeedModule } from './feed/feed.module';

@NgModule({
  declarations: [
    AppComponent,
    UploadMusicComponent,
    ContentOverviewComponent,
    ArtistCreationComponent,
    HomeComponent,
    DiscoverComponent,
    AlbumsCreationComponent,
    ManageContentComponent,
    SubscriptionsComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    MaterialModule,
    AppRoutingModule,
    AuthModule,
    SharedModule,
    FeedModule,
  ],
  providers: [
    provideClientHydration(),
    provideAnimationsAsync(),
    provideHttpClient(withFetch(), withInterceptorsFromDi()),
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
