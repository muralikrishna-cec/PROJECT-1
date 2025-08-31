import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

@Component({
  selector: 'app-batch-processing',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './batch-processing.html',
})
export class BatchProcessingComponent {
  inputType: string = 'github';
  githubUrl: string = '';
  result: any[] = []; // table data
  loading = false;
  error: string = '';
  selectedFile: File | null = null;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  // ✅ Handle file selection
  onFileSelected(event: Event) {
    const fileInput = event.target as HTMLInputElement;
    if (fileInput.files && fileInput.files.length > 0) {
      this.selectedFile = fileInput.files[0];
      this.error = '';
    }
  }

  // ✅ Analyze Batch (GitHub repo or ZIP file)
  analyzeBatch() {
    this.loading = true;
    this.result = [];
    this.error = '';
    this.cdr.detectChanges();

    const apiUrl = 'http://localhost:8000/batch';

    if (this.inputType === 'github') {
      if (!this.githubUrl.trim()) {
        this.error = 'Please enter a GitHub repository URL';
        this.loading = false;
        return;
      }

      const payload = { type: 'github', github_url: this.githubUrl };

      this.http.post(apiUrl, payload, { responseType: 'json' }).subscribe({
        next: (res: any) => this.handleResponse(res),
        error: (err) => this.handleError(err),
      });
    } else if (this.inputType === 'file') {
      if (!this.selectedFile) {
        this.error = 'Please select a ZIP file';
        this.loading = false;
        return;
      }

      const formData = new FormData();
      formData.append('type', 'file');
      formData.append('file', this.selectedFile);

      this.http.post(apiUrl, formData, { responseType: 'json' }).subscribe({
        next: (res: any) => this.handleResponse(res),
        error: (err) => this.handleError(err),
      });
    }
  }

  // ✅ Handle API response
private handleResponse(res: any) {
  if (!res || !Array.isArray(res.files)) {
    this.error = 'Unexpected response format';
    this.loading = false;
    this.cdr.detectChanges();
    return;
  }

  this.result = res.files.map((file: any) => {
    const m = file.metrics?.metrics || {}; // numeric metrics

    return {
      path: file.path,
      language: file.language,
      classes: m.classes || 0,
      methods: m.functions || 0,         // functions → methods
      lines_of_code: m.loc || 0,         // loc → lines_of_code
      comments: m.comments || 0,
      cyclomatic_complexity: m.cyclomatic_complexity || 0,
      quality_score: m.quality_score || 0,
      note: (file.metrics?.suggestions?.join('; ')) || '-', // suggestions as note
    };
  });

  this.loading = false;
  this.cdr.detectChanges();
}





  // ✅ Handle API errors
  private handleError(err: any) {
    this.error = `⚠️ Service unavailable. Error: ${err.message || 'Unknown error'}`;
    this.loading = false;
    this.cdr.detectChanges();
  }

  // ✅ Export table as PDF using jsPDF
 


exportPDF() {
  if (!this.result || this.result.length === 0) {
    this.error = 'No data available to export';
    return;
  }

  const doc = new jsPDF();

  doc.setFontSize(16);
  doc.text('📦 Batch Processing Report', 14, 20);

  // Table headers
  const headers = [
    'Path',
    'Language',
    'Classes',
    'Methods',
    'LOC',
    'Comments',
    'Cyclomatic Complexity',
    'Quality Score',
    'Note'
  ];

  // Table body
  const body = this.result.map(row => [
    row.path || '-',
    row.language || '-',
    row.classes ?? 0,
    row.methods ?? 0,
    row.lines_of_code ?? 0,
    row.comments ?? 0,
    row.cyclomatic_complexity ?? 0,
    `${row.quality_score ?? 0}%`,
    Array.isArray(row.note) ? row.note.join('; ') : row.note || '-'
  ]);

  autoTable(doc, {
    startY: 30,
    head: [headers],
    body: body,
    styles: { fontSize: 10 },
    headStyles: { fillColor: [22, 160, 133], textColor: 255 },
    alternateRowStyles: { fillColor: [240, 240, 240] },
    margin: { top: 30 }
  });

  doc.save('batch-report.pdf');
}



  // ✅ Style notes column
  getNoteClass(note: string) {
    if (!note) return '';
    if (note.toLowerCase().includes('good')) return 'text-green-600 font-semibold';
    if (note.toLowerCase().includes('improve')) return 'text-yellow-600 font-semibold';
    if (note.toLowerCase().includes('bad') || note.toLowerCase().includes('error'))
      return 'text-red-600 font-semibold';
    return '';
  }
}
