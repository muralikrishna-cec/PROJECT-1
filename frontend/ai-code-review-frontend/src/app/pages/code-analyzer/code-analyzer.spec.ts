import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CodeAnalyzer } from './code-analyzer';

describe('CodeAnalyzer', () => {
  let component: CodeAnalyzer;
  let fixture: ComponentFixture<CodeAnalyzer>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CodeAnalyzer]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CodeAnalyzer);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
