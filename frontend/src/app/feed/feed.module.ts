import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { FeedPageComponent } from './feed/feed.component';

@NgModule({
  declarations: [FeedPageComponent],
  imports: [CommonModule, HttpClientModule],
})
export class FeedModule { }
