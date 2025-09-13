import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ArtistCreationComponent } from './artist-creation.component';

describe('ArtistCreationComponent', () => {
  let component: ArtistCreationComponent;
  let fixture: ComponentFixture<ArtistCreationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ArtistCreationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ArtistCreationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
