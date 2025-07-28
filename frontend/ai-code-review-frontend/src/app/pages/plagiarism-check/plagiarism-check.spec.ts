import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlagiarismCheck } from './plagiarism-check';

describe('PlagiarismCheck', () => {
  let component: PlagiarismCheck;
  let fixture: ComponentFixture<PlagiarismCheck>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PlagiarismCheck]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PlagiarismCheck);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
