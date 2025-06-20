import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Drugs } from './drugs';

describe('Drugs', () => {
  let component: Drugs;
  let fixture: ComponentFixture<Drugs>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Drugs]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Drugs);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
