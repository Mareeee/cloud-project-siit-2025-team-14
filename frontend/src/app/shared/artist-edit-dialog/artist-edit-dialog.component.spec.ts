import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ArtistEditDialogComponent } from './artist-edit-dialog.component';

describe('ArtistEditDialogComponent', () => {
  let component: ArtistEditDialogComponent;
  let fixture: ComponentFixture<ArtistEditDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ArtistEditDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ArtistEditDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
