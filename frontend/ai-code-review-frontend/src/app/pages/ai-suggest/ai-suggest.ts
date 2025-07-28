import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule, HttpClient, HttpHeaders } from '@angular/common/http';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';


@Component({
  standalone: true,
  selector: 'app-ai-suggest',
  templateUrl: './ai-suggest.html',
  styleUrls: ['./ai-suggest.css'],
  imports: [CommonModule, FormsModule, HttpClientModule]
})
export class AiSuggestComponent {
  code: string = '';
  language: string = 'check programming language '; // default
  formattedResponse: SafeHtml = '';
  response: string = '';
  loading: boolean = false;

  constructor(private http: HttpClient, private cd: ChangeDetectorRef,private sanitizer: DomSanitizer) {}

  getSuggestion(): void {
    if (!this.code.trim()) {
      this.response = '❌ Please enter some code.';
      return;
    }

    this.language = this.detectLanguage(this.code);
    this.loading = true;
    this.response = '';

    const payload = {
      language: this.language,
      code: this.code
    };
    console.log(this.language);
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    this.http.post('http://localhost:8080/api/ai-suggest', payload, {
      headers: headers,
      responseType: 'text'
    }).subscribe({
      next: (res: any) => {
        try {
          // If response is a stringified JSON (from Flask, for example), parse it first
          const parsed = typeof res === 'string' ? JSON.parse(res) : res;
      
          if (parsed.response) {
            this.response = parsed.response;
            this.formattedResponse = this.sanitizer.bypassSecurityTrustHtml(
              this.formatResponseToHtml(parsed.response)
            );
          } else {
            this.response = res;
            this.formattedResponse = res;
          }
        } catch (e) {
          // fallback: treat as plain text
          this.response = res;
          this.formattedResponse = this.sanitizer.bypassSecurityTrustHtml(
            this.formatResponseToHtml(res)
          );
        }
      
        this.loading = false;
        this.cd.detectChanges();
      },
      
      error: (err) => {
        this.response = '❌ Failed to connect to AI backend.';
        console.error('[AI Suggestion Error]', err);
        this.loading = false;
        this.cd.detectChanges(); // ✅ force UI refresh
      }
    });
  }
  formatResponseToHtml(text: string): string {
    // Convert ```lang\ncode``` blocks to <pre><code class="language-lang">...</code></pre>
    return text
      .replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang = '', code) => {
        const safeCode = this.escapeHtml(code);
        return `<pre class="bg-gray-900 text-green-400 p-3 rounded overflow-x-auto"><code class="language-${lang}">${safeCode}</code></pre>`;
      })
      .replace(/\n/g, '<br>'); // Optional: handle normal line breaks
  }
  

  escapeHtml(code: string): string {
    return code
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }
  


  detectLanguage(code: string): string {
    const trimmed = code.trim();

    if (/^\s*#include\s+<.*?>/.test(trimmed)) return 'c';
    if (/^\s*#include\s+["<]iostream[">]/.test(trimmed)) return 'cpp';
    if (/^\s*(public\s+class|System\.out\.println)/.test(trimmed)) return 'java';
    if (/^\s*function\s+|console\.log|let\s+|const\s+/.test(trimmed)) return 'javascript';
    if (/^\s*print\(|def\s+|import\s+/.test(trimmed)) return 'python';

    return 'unknown'; // default fallback
  }
}
