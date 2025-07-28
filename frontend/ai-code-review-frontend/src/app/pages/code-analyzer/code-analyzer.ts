import { Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

import { AfterViewInit, Component, AfterViewChecked } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import mermaid from 'mermaid';

@Component({
  standalone: true,
  selector: 'app-code-analyzer',
  templateUrl: './code-analyzer.html',
  styleUrls: ['./code-analyzer.css'],
  imports: [FormsModule, CommonModule, HttpClientModule]
})
export class CodeAnalyzer implements AfterViewInit, AfterViewChecked {
  metrics = {loc: 0,complexity: 0,score: 0 };
  
  userCode: string = '';
  output: string = '';
  formattedOutput: { title: string; body: string }[] = [];
  flowOutput: string = '';
  mermaid: any = null;

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  async ngAfterViewInit(): Promise<void> {
    const mermaidModule = await import('mermaid');
    this.mermaid = mermaidModule.default;
    this.mermaid.initialize({ startOnLoad: false });
  }

  async ngAfterViewChecked(): Promise<void> {
    if (isPlatformBrowser(this.platformId)) {
      const container = document.getElementById('mermaid-container');
      if (container && this.flowOutput.startsWith('graph') && this.mermaid) {
        this.mermaid.init(undefined, container);
      }
    }
  }

  submitCode() {
    const headers = { 'Content-Type': 'text/plain' };
  
    this.http.post('http://localhost:8080/api/analyze', this.userCode, {
      headers,
      responseType: 'text'
    }).subscribe({
      next: (res) => {
        this.output = res;
        console.log('[Raw Backend Output]', res.substring(0, 500));
        
        this.formattedOutput = this.formatOutput(res);
  
        // ✅ Extract flow output cleanly
        const flowStartIndex = res.indexOf('🔍 Code Flow Visualization:');
        if (flowStartIndex !== -1) {
          this.flowOutput = res.substring(flowStartIndex + '🔍 Code Flow Visualization:'.length).trim();
  
          // 🧼 Remove any HTML-like tags that might break Mermaid parsing
          this.flowOutput = this.flowOutput.replace(/<\/?[^>]+(>|$)/g, '');
  
          console.log('[✅ Mermaid Flow Extracted]', this.flowOutput);
        } else {
          this.flowOutput = '';
          console.warn('[❌ Mermaid] Flow section not found in response.');
        }
  
        this.renderMermaid();
      },
      
      error: (err) => {
        this.output = '❌ Failed to connect to backend.';
        console.error(err);
      }
    });
  }
  


  getStrokeOffset(score: number): number {
    const radius = 45;
    const circumference = 2 * Math.PI * radius;
    return circumference - (score / 100) * circumference;
  }
  

  formatOutput(text: string): any[] {
    const sections = text.split('\n\n');
    const output: { title: string, body: string }[] = [];

  
    sections.forEach(section => {
      const lines = section.trim().split('\n');
      const title = lines[0]?.trim();
      const body = lines.slice(1).join('\n');
    
      if (title.includes('🔍 Code Flow Visualization')) {
        return; // Skip, we assign this separately
      }
    
      // Parse metrics
      if (title.includes('📊 Code Metrics')) {
       // const locMatch = body.match(/LOC: (\d+)/);
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
  
  getCircumference(radius: number): number {
    return 2 * Math.PI * radius;
  }
  
  renderMermaid() {
    if (!this.flowOutput || !this.flowOutput.trim().startsWith('graph')) {
      console.warn('[Mermaid] No valid flowOutput found in response.');
      return;
    }
  
    if (isPlatformBrowser(this.platformId)) {
      const container = document.getElementById('mermaid-container');
      console.log('[Mermaid] Mermaid container exists?', !!container);
  
      if (container) {
        // ✅ Clear previous content
        container.innerHTML = '';
  
        // ✅ Create dynamic element
        const chartEl = document.createElement('div');
        chartEl.className = 'mermaid';
        chartEl.innerHTML = this.flowOutput;
  
        container.appendChild(chartEl);
  
        // ✅ Init just this new element
        //this.mermaid.init(undefined, chartEl);
       // ✅ Use requestAnimationFrame instead of setTimeout
      requestAnimationFrame(() => {
        this.mermaid.init(undefined, chartEl);
      });
        
      }
    } else {
      console.warn('[Mermaid] Skipped rendering: running on server (SSR)');
    }
  }
  

  copyReport() {
    const fullReport = this.formattedOutput
      .map(section => `${section.title}\n${section.body}`)
      .join('\n\n');

    navigator.clipboard.writeText(fullReport).then(() => {
      alert("📋 Report copied to clipboard!");
    });
  }
}