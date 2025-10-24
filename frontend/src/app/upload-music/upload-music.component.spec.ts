import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UploadMusicComponent } from './upload-music.component';

describe('UploadMusicComponent', () => {
  let component: UploadMusicComponent;
  let fixture: ComponentFixture<UploadMusicComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [UploadMusicComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UploadMusicComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
