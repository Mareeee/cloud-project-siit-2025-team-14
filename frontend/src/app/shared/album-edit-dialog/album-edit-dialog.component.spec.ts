import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AlbumEditDialogComponent } from './album-edit-dialog.component';

describe('AlbumEditDialogComponent', () => {
  let component: AlbumEditDialogComponent;
  let fixture: ComponentFixture<AlbumEditDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AlbumEditDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AlbumEditDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
