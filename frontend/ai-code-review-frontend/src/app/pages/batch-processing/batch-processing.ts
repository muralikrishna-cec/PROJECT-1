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
    const m = file.metrics || {};

    return {
      path: file.path,
      language: file.language,

      // 🔹 Metrics
      assignments: m.assignments || 0,
      classes: m.classes || 0,
      functions: m.functions || 0,
      function_calls: m.function_calls || 0,
      loc: m.loc || 0,
      loops: m.loops || 0,
      max_nesting: m.max_nesting || 0,
      operators: m.operators || 0,
      returns: m.returns || 0,
      comments: m.comments || 0,
      cyclomatic_complexity: m.cyclomatic_complexity || 0,
      quality_score: m.quality_score || 0,

      // 🔹 AI Suggestions
      suggestions: (file.suggestions?.join('; ')) || '-',

      // 🔹 Syntax Errors
      syntax_errors:
        file.syntax_errors && file.syntax_errors.length > 0
          ? file.syntax_errors.join('\n')
          : '-',

      // 🔹 Logic Issues
      logic_issues:
        file.logic_issues && file.logic_issues.length > 0
          ? file.logic_issues.join('\n')
          : '-'
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

  // ✅ Build table body with all fields
  const body: any[] = [];

  this.result.forEach((file, index) => {
    body.push([
      {
        content: `#${index + 1}  ${file.path || '-'}`,
        colSpan: 2,
        styles: { halign: 'left', fillColor: [230, 230, 250] }
      }
    ]);

    body.push(['Language', file.language || '-']);
    body.push(['Assignments', file.assignments ?? 0]);
    body.push(['Classes', file.classes ?? 0]);
    body.push(['Functions', file.functions ?? 0]);
    body.push(['Function Calls', file.function_calls ?? 0]);
    body.push(['Lines of Code', file.loc ?? file.lines_of_code ?? 0]);
    body.push(['Loops', file.loops ?? 0]);
    body.push(['Max Nesting', file.max_nesting ?? 0]);
    body.push(['Operators', file.operators ?? 0]);
    body.push(['Returns', file.returns ?? 0]);
    body.push(['Comments', file.comments ?? 0]);
    body.push(['Cyclomatic Complexity', file.cyclomatic_complexity ?? 0]);
    body.push(['Quality Score', `${file.quality_score ?? 0}%`]);

    body.push([
      'Note',
      Array.isArray(file.note) ? file.note.join('; ') : file.note || '-'
    ]);
    body.push([
      'Suggestions',
      Array.isArray(file.suggestions) ? file.suggestions.join('; ') : file.suggestions || '-'
    ]);
    body.push([
      'Syntax Errors',
      Array.isArray(file.syntax_errors) ? file.syntax_errors.join('\n') : file.syntax_errors || '-'
    ]);
    body.push([
      'Logic Issues',
      Array.isArray(file.logic_issues) ? file.logic_issues.join('\n') : file.logic_issues || '-'
    ]);

    // ✅ Add separator between files
    body.push([{ content: '', colSpan: 2, styles: { fillColor: [255, 255, 255] } }]);
  });

  autoTable(doc, {
    startY: 30,
    head: [['Field', 'Value']],
    body: body,
    theme: 'grid',
    styles: { fontSize: 10, cellPadding: 3, valign: 'top' },
    headStyles: { fillColor: [22, 160, 133], textColor: 255 },
    alternateRowStyles: { fillColor: [245, 245, 245] },
    columnStyles: {
      0: { cellWidth: 60, fontStyle: 'bold' }, // Field column
      1: { cellWidth: 120 } // Value column
    },
    margin: { top: 30 },
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
