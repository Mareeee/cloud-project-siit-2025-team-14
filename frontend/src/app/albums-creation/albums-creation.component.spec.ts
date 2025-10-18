import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AlbumsCreationComponent } from './albums-creation.component';

describe('AlbumsCreationComponent', () => {
  let component: AlbumsCreationComponent;
  let fixture: ComponentFixture<AlbumsCreationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AlbumsCreationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AlbumsCreationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
