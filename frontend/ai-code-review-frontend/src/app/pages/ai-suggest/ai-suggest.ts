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
  language: string = 'check programming language';
  formattedResponse: SafeHtml = '';
  responseLines: string[] = [];
  displayedLines: string[] = [];
  loading: boolean = false;

  private typingInterval: any = null;
  private isTyping: boolean = false;

  constructor(
    private http: HttpClient,
    private cd: ChangeDetectorRef,
    private sanitizer: DomSanitizer
  ) {}



getSuggestion(): void {
  this.displayedLines = [];
  this.responseLines = [];
  this.formattedResponse = '';
  this.cd.detectChanges();
  this.isTyping = false;

  if (!this.code.trim()) {
    this.displayedLines = ['❌ Please enter some code.'];
    this.updateFormattedResponse();
    return;
  }

  if (this.typingInterval) {
    clearInterval(this.typingInterval);
    this.typingInterval = null;
  }

  this.language = this.detectLanguage(this.code);
  this.loading = true;

  const payload = { language: this.language, code: this.code };
  const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

  this.http.post('http://localhost:8080/api/ai-suggest', payload, {
    headers,
    responseType: 'text'
  }).subscribe({
    next: (res: any) => {
      let fullText: string = '';
      try {
        const parsed = typeof res === 'string' ? JSON.parse(res) : res;
        fullText = parsed.response || res;
      } catch {
        fullText = res;
      }

      this.responseLines = fullText.split(/\r?\n/).filter(l => l.trim() !== '');
      this.displayedLines = [];
      this.isTyping = true;

      this.startTypingAnimation().then(() => {
        this.loading = false;
        this.isTyping = false;
      });
    },
    error: () => {
      // ✅ Always show a clean, user-friendly message
      this.displayedLines = [
        '⚠️ AI Suggestion service is not available at the moment.',
        '🔄 Please try again later.'
      ];
      this.updateFormattedResponse();
      this.loading = false;
    }
  });
}






  private async startTypingAnimation(): Promise<void> {
    for (const line of this.responseLines) {
      await this.typeLine(line);
    }
  }

  private typeLine(line: string): Promise<void> {
    return new Promise<void>((resolve) => {
      let i = 0;
      this.displayedLines.push(''); // start new line

      this.typingInterval = setInterval(() => {
        this.displayedLines[this.displayedLines.length - 1] += line[i];
        this.updateFormattedResponse();
        i++;

        if (i >= line.length) {
          clearInterval(this.typingInterval);
          this.typingInterval = null;
          setTimeout(() => resolve(), 150); // small pause between lines
        }
      }, 30); // typing speed
    });
  }

  private updateFormattedResponse(): void {
    const html = this.displayedLines
      .map(l => this.formatResponseToHtml(l))
      .join('<br>');
    this.formattedResponse = this.sanitizer.bypassSecurityTrustHtml(html);
    this.cd.detectChanges();
  }

  formatResponseToHtml(text: string): string {
    return text
      .replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang = '', code) => {
        const safeCode = this.escapeHtml(code);
        return `<pre class="bg-gray-900 text-green-400 p-3 rounded overflow-x-auto"><code class="language-${lang}">${safeCode}</code></pre>`;
      })
      .replace(/\n/g, '<br>');
  }

  escapeHtml(code: string): string {
    return code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  detectLanguage(code: string): string {
    const trimmed = code.trim();
    if (/^\s*#include\s+<.*?>/.test(trimmed)) return 'c';
    if (/^\s*#include\s+["<]iostream[">]/.test(trimmed)) return 'cpp';
    if (/^\s*(public\s+class|System\.out\.println)/.test(trimmed)) return 'java';
    if (/^\s*function\s+|console\.log|let\s+|const\s+/.test(trimmed)) return 'javascript';
    if (/^\s*print\(|def\s+|import\s+/.test(trimmed)) return 'python';
    return 'unknown';
  }
}
