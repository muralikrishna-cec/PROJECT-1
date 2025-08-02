import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlagiarismCheckComponent } from './plagiarism-check';

describe('PlagiarismCheck', () => {
  let component: PlagiarismCheckComponent;
  let fixture: ComponentFixture<PlagiarismCheckComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PlagiarismCheckComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PlagiarismCheckComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
