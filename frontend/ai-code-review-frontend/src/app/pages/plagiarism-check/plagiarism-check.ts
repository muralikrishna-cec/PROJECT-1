import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule, HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  standalone: true,
  selector: 'app-plagiarism-check',
  templateUrl: './plagiarism-check.html',
  styleUrls: ['./plagiarism-check.css'],
  imports: [CommonModule, FormsModule, HttpClientModule]
})
export class PlagiarismCheckComponent {
  code1: string = '';
  code2: string = '';
  result: string = '';
  loading: boolean = false;

  constructor(
    private http: HttpClient,
    private cdr: ChangeDetectorRef  // ✅ Add ChangeDetectorRef to force refresh
  ) {}

  checkPlagiarism(): void {
    if (!this.code1.trim() || !this.code2.trim()) {
      this.result = '❌ Please enter both code snippets.';
      return;
    }

    this.loading = true;
    this.result = '';

    const payload = {
      code1: this.code1,
      code2: this.code2
    };

    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    this.http.post('http://localhost:8080/api/plagiarism', payload, {
      headers: headers,
      responseType: 'text'
    }).subscribe({
      next: (res: string) => {
        this.result = res;
        this.loading = false;
       // console.log('[✅ Response]', res);

        this.cdr.detectChanges(); // ✅ Manually trigger UI update
        //alert('✅ Result Received!');
      },
      error: (err) => {
        this.result = '❌ Error connecting to backend.';
        console.error('[Plagiarism Error]', err);
        this.loading = false;
        this.cdr.detectChanges(); // Ensure UI reflects error too
      }
    });
  }
}
