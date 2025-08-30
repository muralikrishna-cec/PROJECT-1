import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-batch-processing',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './batch-processing.html',
})
export class BatchProcessingComponent {
  inputType: string = 'github';
  githubUrl: string = '';
  result: any[] = []; // store array of items for table
  loading = false;
  errorMessage: string = '';

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

analyzeBatch() {
  if (!this.githubUrl.trim()) {
    this.errorMessage = 'Please enter a GitHub repository URL';
    return;
  }

  this.loading = true;
  this.result = [];
  this.errorMessage = '';
  this.cdr.detectChanges();

  const payload = { type: 'github', github_url: this.githubUrl };
  const apiUrl = 'http://localhost:8000/batch';

  this.http.post(apiUrl, payload, { responseType: 'json' }).subscribe({
    next: (res: any) => {
      // Flatten the "files" array from the backend
      if (res && Array.isArray(res.files)) {
        this.result = res.files.map((file: any) => ({
          path: file.path,
          language: file.language,
          classes: file.metrics?.classes || 0,
          loc: file.metrics?.loc || 0,
          methods: file.metrics?.methods || 0,
          note: file.metrics?.note || ''
        }));
      } else {
        this.errorMessage = 'Unexpected response format';
      }

      this.loading = false;
      this.cdr.detectChanges();
    },
    error: (err) => {
      this.errorMessage = `⚠️ Service unavailable. Error: ${err.message || 'Unknown error'}`;
      this.loading = false;
      this.cdr.detectChanges();
    }
  });
}

}
