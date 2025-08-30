import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BatchProcessingComponent } from './batch-processing';

describe('BatchProcessing', () => {
  let component: BatchProcessingComponent;
  let fixture: ComponentFixture<BatchProcessingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BatchProcessingComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BatchProcessingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
