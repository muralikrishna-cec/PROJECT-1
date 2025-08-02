import {
  AfterViewInit,
  Component,
  ElementRef,
  Inject,
  PLATFORM_ID,
  ViewChild
} from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import * as monaco from 'monaco-editor';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-plagiarism-checker',
  standalone: true,
  imports: [FormsModule, HttpClientModule, CommonModule],
  templateUrl: './plagiarism-check.html'
})
export class PlagiarismCheckComponent implements AfterViewInit {
  @ViewChild('editor1Container', { static: false }) editor1Container!: ElementRef;
  @ViewChild('editor2Container', { static: false }) editor2Container!: ElementRef;

  monacoEditor1!: monaco.editor.IStandaloneCodeEditor;
  monacoEditor2!: monaco.editor.IStandaloneCodeEditor;

  code1: string = '';
  code2: string = '';
  selectedLanguage: string = 'python';
  result: any = '';
  loading = false;

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object,
    private cdr: ChangeDetectorRef 
  ) {}

  ngAfterViewInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.monacoEditor1 = monaco.editor.create(this.editor1Container.nativeElement, {
        value: this.code1,
        language: this.selectedLanguage,
        theme: 'vs-dark',
        automaticLayout: true
      });

      this.monacoEditor2 = monaco.editor.create(this.editor2Container.nativeElement, {
        value: this.code2,
        language: this.selectedLanguage,
        theme: 'vs-dark',
        automaticLayout: true
      });
    }
  }

  onLangChange(event: Event) {
    const lang = (event.target as HTMLSelectElement).value;
    this.selectedLanguage = lang;
    if (this.monacoEditor1 && this.monacoEditor2) {
      monaco.editor.setModelLanguage(this.monacoEditor1.getModel()!, lang);
      monaco.editor.setModelLanguage(this.monacoEditor2.getModel()!, lang);
    }
  }

  checkPlagiarism() {
  this.loading = true;
  this.result = '';
  this.cdr.detectChanges(); // Show "Checking..."

  const code1 = this.monacoEditor1.getValue();
  const code2 = this.monacoEditor2.getValue();

  const payload = {
    code1,
    code2,
    language: this.selectedLanguage
  };

  // ✅ Choose correct backend based on language
 const apiUrl = 'http://localhost:8080/api/plagiarism';


  this.http.post(apiUrl, payload, { responseType: 'text' }).subscribe({
    next: res => {
      try {
        const parsed = JSON.parse(res);
        this.result = parsed;
      } catch (e) {
        this.result = {
          verdict: '❌ Could not parse server response.',
          error: res
        };
      }
      this.loading = false;
      this.cdr.detectChanges();
    },
    error: err => {
      this.result = {
        verdict: '❌ Error contacting backend.',
        error: err.message || 'Unknown error'
      };
      this.loading = false;
      this.cdr.detectChanges();
    }
  });
}


}
