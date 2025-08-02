import {
  AfterViewInit,
  Component,
  Inject,
  PLATFORM_ID,
  ViewChild,
  ElementRef,
  ChangeDetectorRef
} from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import * as monaco from 'monaco-editor';
import mermaid from 'mermaid';

@Component({
  standalone: true,
  selector: 'app-code-analyzer',
  templateUrl: './code-analyzer.html',
  styleUrls: ['./code-analyzer.css'],
  imports: [FormsModule, CommonModule, HttpClientModule]
})
export class CodeAnalyzer implements AfterViewInit {
  @ViewChild('editorContainer', { static: false }) editorContainer!: ElementRef;

  selectedLang: string = 'java';
  userCode: string = '';
  activeTab: 'analysis' | 'visualization' | 'suggestions' = 'analysis';
  aiSuggestionText: string = '';
  parsedSuggestions: { title: string; items: string[] }[] = [];

  metrics = { loc: 0, complexity: 0, score: 0 };
  formattedOutput: { title: string; body: string }[] = [];
  flowOutput: string = '';
  output: string = '';
  monacoEditorInstance!: monaco.editor.IStandaloneCodeEditor;
  mermaid: any;

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object,
    private cdr: ChangeDetectorRef
  ) {}

  ngAfterViewInit() {
    this.mermaid = mermaid;
    this.mermaid.initialize({
      startOnLoad: false,
      theme: 'base',
      securityLevel: 'loose',
      themeVariables: {
        primaryColor: '#cce5ff',
        primaryTextColor: '#002b36',
        primaryBorderColor: '#3399cc',
        secondaryColor: '#d0f0fd',
        tertiaryColor: '#f3fbff',
        fontFamily: 'Segoe UI, Inter, sans-serif',
        fontSize: '10px',
        edgeLabelBackground: '#ffffff',
        textColor: '#002b36',
        nodeBorder: 'round',
        clusterBkg: '#f0f8ff',
        clusterBorder: '#3399cc',
        lineColor: '#66c2ff'
      },
      flowchart: {
        curve: 'basis',
        useMaxWidth: true,
        htmlLabels: true,
        padding: 10,
        nodeSpacing: 40,
        rankSpacing: 70,
        defaultRenderer: 'dagre'
      }
    });

    if (isPlatformBrowser(this.platformId)) {
      this.monacoEditorInstance = monaco.editor.create(this.editorContainer.nativeElement, {
        value: this.userCode,
        language: this.selectedLang,
        theme: 'vs-dark',
        automaticLayout: true
      });
    }
  }

  onLangChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    if (target && target.value && this.monacoEditorInstance) {
      this.selectedLang = target.value;
      monaco.editor.setModelLanguage(this.monacoEditorInstance.getModel()!, target.value);
    }
  }

  submitCode(): void {
    const code = this.monacoEditorInstance.getValue();
    const payload = { language: this.selectedLang, code };

    this.http.post('http://localhost:8080/api/analyze', payload, {
      headers: { 'Content-Type': 'application/json' },
      responseType: 'text'
    }).subscribe({
      next: (res) => {
        this.output = res;
        this.formattedOutput = this.formatOutput(res);

        const flowStartIndex = res.indexOf('🔍 Code Flow Visualization:');
        if (flowStartIndex !== -1) {
          this.flowOutput = this.sanitizeFlowOutput(
            res.substring(flowStartIndex + '🔍 Code Flow Visualization:'.length).trim()
          );
        }

        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Backend error:', err);
        this.output = '❌ Backend connection failed.';
      }
    });
  }

  fetchAISuggestions(): void {
    const code = this.monacoEditorInstance.getValue();
    const payload = { code, language: this.selectedLang };

    this.http.post<any>('http://localhost:8080/api/ai-suggest', payload).subscribe({
      next: (res) => {
        this.aiSuggestionText = res.response || '';
        this.parsedSuggestions = this.formatAISuggestions(this.aiSuggestionText);
        this.setActiveTab('suggestions');
      },
      error: () => {
        this.aiSuggestionText = '';
        this.parsedSuggestions = [];
        alert('❌ Failed to fetch AI suggestions.');
      }
    });
  }

  formatAISuggestions(raw: string): { title: string, items: string[] }[] {
    const sections = raw.split(/\n\n(?=[A-Za-z ]+:\n)/);
    return sections.map(section => {
      const lines = section.trim().split('\n');
      const titleLine = lines.shift()?.replace(':', '').trim() || 'Suggestions';
      const points = lines
        .filter(line => line.trim().length > 0)
        .map(line => line.replace(/^\d+\.\s*/, '• ').trim());
      return { title: titleLine, items: points };
    });
  }

  sanitizeFlowOutput(raw: string): string {
    const cleanedLines = raw
      .replace(/<\/?[^>]+(>|$)/g, '')
      .replace(/[\u{FE00}-\u{FE0F}]/gu, '')
      .replace(/[\u{1F300}-\u{1FAFF}|\u{1F600}-\u{1F6FF}|\u{2600}-\u{26FF}|\u{2700}-\u{27BF}]/gu, '')
      .replace(/📦/g, 'Class')
      .replace(/🔧/g, 'Method')
      .replace(/🖨️/g, 'Print')
      .replace(/🔁/g, 'Loop')
      .replace(/🔸/g, 'Stmt')
      .split('\n')
      .map(line => {
        const trimmed = line.trim();
        return trimmed ? (trimmed.endsWith(';') ? trimmed : trimmed + ';') : '';
      });

    if (!cleanedLines[0].includes('graph')) {
      cleanedLines.unshift('graph TD;');
    }

    return cleanedLines.join('\n');
  }

  formatOutput(text: string): { title: string, body: string }[] {
    const sections = text.split('\n\n');
    const output: { title: string, body: string }[] = [];

    sections.forEach(section => {
      const lines = section.trim().split('\n');
      const title = lines[0]?.trim();
      const body = lines.slice(1).join('\n');

      if (title.includes('🔍 Code Flow Visualization')) return;

      if (title.includes('📊 Code Metrics')) {
        const locMatch = body.match(/Lines of Code \(LOC\): (\d+)/);
        const complexityMatch = body.match(/Complexity: (\d+)/);
        const scoreMatch = body.match(/Score: (\d+)%/);

        this.metrics.loc = locMatch ? +locMatch[1] : 0;
        this.metrics.complexity = complexityMatch ? +complexityMatch[1] : 0;
        this.metrics.score = scoreMatch ? +scoreMatch[1] : 0;
      }

      output.push({ title, body });
    });

    return output;
  }

  renderMermaid() {
    const graph = this.flowOutput?.trim();
    if (!graph || !graph.startsWith('graph')) return;

    const container = document.getElementById('mermaid-container');
    if (!container) return;

    container.innerHTML = '';
    const chartEl = document.createElement('div');
    chartEl.className = 'mermaid';
    chartEl.innerHTML = graph;
    container.appendChild(chartEl);

    requestAnimationFrame(() => {
      try {
        this.mermaid.parse(graph);
        this.mermaid.init(undefined, chartEl);
      } catch (err) {
        console.error('[❌ Mermaid Render Error]', err);
      }
    });
  }

  setActiveTab(tab: 'analysis' | 'visualization' | 'suggestions') {
    this.activeTab = tab;
    this.cdr.detectChanges();
    if (tab === 'visualization' && this.flowOutput?.trim().startsWith('graph')) {
      setTimeout(() => this.renderMermaid(), 100);
    }
  }

  copyReport(): void {
    const fullReport = this.formattedOutput
      .map(section => `${section.title}\n${section.body}`)
      .join('\n\n');
    navigator.clipboard.writeText(fullReport).then(() => {
      alert('📋 Report copied to clipboard!');
    });
  }

  copySuggestion(): void {
    navigator.clipboard.writeText(this.aiSuggestionText).then(() => {
      alert('📋 AI Suggestion copied to clipboard!');
    });
  }

  getStrokeOffset(score: number): number {
    const r = 45;
    const circumference = 2 * Math.PI * r;
    return circumference - (score / 100) * circumference;
  }

  getCircumference(r: number): number {
    return 2 * Math.PI * r;
  }
}
