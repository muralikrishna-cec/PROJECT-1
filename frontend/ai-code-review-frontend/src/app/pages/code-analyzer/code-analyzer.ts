import {
  AfterViewInit,
  AfterViewChecked,
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
import { lastValueFrom } from 'rxjs';
import * as monaco from 'monaco-editor';
import * as d3 from 'd3';
import { marked } from 'marked';

interface GraphNode { id: string; type: string; label: string }
interface GraphEdge { from: string; to: string; condition?: string }

interface D3Node extends GraphNode { x?: number; y?: number; vx?: number; vy?: number; fx?: number | null; fy?: number | null; }
interface D3Edge extends GraphEdge { source: D3Node; target: D3Node; }

interface AnalysisResponse {
  nodes?: GraphNode[];
  edges?: GraphEdge[];
  metrics?: { loc?: number; functions?: number; cyclomatic_complexity?: number; quality_score?: string | number };
  report?: string;
  suggestions?: string | string[];
  analysis?: string;
  viva?: string | string[];
}

@Component({
  standalone: true,
  selector: 'app-code-analyzer',
  templateUrl: './code-analyzer.html',
  styleUrls: ['./code-analyzer.css'],
  imports: [FormsModule, CommonModule, HttpClientModule]
})
export class CodeAnalyzer implements AfterViewInit, AfterViewChecked {
  @ViewChild('editorContainer', { static: false }) editorContainer!: ElementRef;

  selectedLang = 'python';
  userCode = '';
  activeTab: 'analysis' | 'visualization' | 'suggestions' | 'viva' = 'analysis';
  metrics = { loc: 0, complexity: 0, functions: 0, score: 0 };
  formattedOutput: { title: string; content: string }[] = [];
  outputRaw: AnalysisResponse | null = null;


// Viva-related properties
vivaLoading = false;                   // true while fetching questions
vivaSubmitted = false;                 // true after submitting answers
vivaQuestions: { question: string; options: string[]; answer: string; }[] = [];
vivaAnswers: (string | null)[] = [];
vivaWarning: string = '';

vivaResult = '';                       // HTML result
totalMarks = 0;                        // total marks possible
marksPerQuestion = 1;                  // default marks per question


  aiSuggestions: string[] = [];
  displayedSuggestions: string[] = [];
  isTyping = false;
  private typingInterval: any = null;

  private monacoEditorInstance!: monaco.editor.IStandaloneCodeEditor;
  private svg!: d3.Selection<SVGSVGElement, unknown, HTMLElement, any>;
  private nodeElements!: d3.Selection<SVGPathElement, d3.HierarchyNode<GraphNode>, SVGGElement, unknown>;
  private linkElements!: d3.Selection<SVGLineElement, d3.HierarchyLink<GraphNode>, SVGGElement, unknown>;

  isPlaying = false;
  private stepIndex = 0;
  private timerRef: any = null;
  speedMs = 900;
  private nodeOrder: string[] = [];
  private edgesOrder: { from: string; to: string }[] = [];
  private graphRendered = false;

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object,
    private cdr: ChangeDetectorRef
  ) {}

  ngAfterViewInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.monacoEditorInstance = monaco.editor.create(this.editorContainer.nativeElement, {
        value: this.userCode,
        language: this.mapLangToMonaco(this.selectedLang),
        theme: 'vs-dark',
        automaticLayout: true
      });
    }
  }

  ngAfterViewChecked() {
    if (this.activeTab === 'visualization' && this.outputRaw?.nodes && this.outputRaw?.edges && !this.graphRendered) {
      d3.select('#graph-container').selectAll('*').remove();
      this.renderAndPrepareGraph(this.outputRaw.nodes, this.outputRaw.edges);
      this.graphRendered = true;
      this.cdr.detectChanges();
    }
  }

  private mapLangToMonaco(lang: string): string {
    const l = lang.toLowerCase();
    if (l === 'c++' || l === 'cpp') return 'cpp';
    if (l === 'c') return 'c';
    if (l === 'python' || l === 'py') return 'python';
    if (l === 'javascript' || l === 'js') return 'javascript';
    if (l === 'typescript' || l === 'ts') return 'typescript';
    return l;
  }

  onLangChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    if (target?.value && this.monacoEditorInstance) {
      this.selectedLang = target.value;
      monaco.editor.setModelLanguage(this.monacoEditorInstance.getModel()!, this.mapLangToMonaco(target.value));
    }
  }

submitCode(): void {
  if (!this.monacoEditorInstance) return;
  const code = this.monacoEditorInstance.getValue();
  const payload = { language: this.selectedLang, code };

  // reset AI suggestions
  this.displayedSuggestions = [];
  this.aiSuggestions = [];
  this.isTyping = false;
  if (this.typingInterval) clearInterval(this.typingInterval);

  // ✅ Reset viva state on new code submission
  this.vivaLoading = false;
  this.vivaSubmitted = false;
  this.vivaQuestions = [];
  this.vivaAnswers = [];
  this.vivaResult = '';

  this.http.post<AnalysisResponse>('http://localhost:8080/api/analyze', payload).subscribe({
    next: (res) => {
      this.outputRaw = res;
      this.populateMetricsAndReport(res);

      this.graphRendered = false;
      this.stepIndex = 0;
      d3.select('#graph-container').selectAll('*').remove();
      this.activeTab = 'analysis';
      this.cdr.detectChanges();
    },
    error: (err) => {
      console.error('Backend error:', err);
      alert('❌ Backend connection failed.');
      this.cdr.detectChanges();
    }
  });
}


  private populateMetricsAndReport(res: AnalysisResponse) {
    const m = res.metrics || {};
    const score = typeof m.quality_score === 'string' ? parseInt(m.quality_score, 10) : Number(m.quality_score ?? 0);
    this.metrics = {
      loc: Number(m.loc ?? 0),
      complexity: Number(m.cyclomatic_complexity ?? 0),
      functions: Number(m.functions ?? 0),
      score: isFinite(score) ? score : 0
    };
    const reportText = (res.report?.trim()) || (res.analysis?.trim()) || 'No report available.';
    this.formattedOutput = [{ title: 'Static Report', content: marked.parse(reportText) as string }];
    this.cdr.detectChanges();
  }

  setActiveTab(tab: 'analysis' | 'visualization' | 'suggestions' | 'viva') {
    this.activeTab = tab;
    this.cdr.detectChanges();

    if (tab === 'visualization' && this.outputRaw?.nodes && this.outputRaw?.edges) {
      d3.select('#graph-container').selectAll('*').remove();
      this.renderAndPrepareGraph(this.outputRaw.nodes, this.outputRaw.edges);
      this.graphRendered = true;
      this.cdr.detectChanges();
    }
  }

  /* ----------------- D3 Graph & Animation ----------------- */
  private renderAndPrepareGraph(nodes: GraphNode[], edges: GraphEdge[]) {
    this.renderD3Graph(nodes, edges);
    this.prepareAnimation(nodes, edges);
    this.resetD3();
    this.cdr.detectChanges();
  }

  private renderD3Graph(nodes: GraphNode[], edges: GraphEdge[]) {
    const container = d3.select('#graph-container');
    container.selectAll('*').remove();
    const el = container.node() as HTMLElement;
    const width = el.clientWidth || 800;
    const height = el.clientHeight || 600;

    this.svg = container.append('svg')
      .attr('width', width)
      .attr('height', height);

    // Arrow markers
    this.svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 15)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#60a5fa');

    const padding = { top: 50, right: 50, bottom: 50, left: 50 };

    const root: d3.HierarchyNode<GraphNode> = d3.stratify<GraphNode>()
      .id(d => d.id)
      .parentId(d => edges.find(e => e.to === d.id)?.from ?? null)(nodes as any);

    const treeLayout = d3.tree<GraphNode>().nodeSize([200, 120]);
    treeLayout(root);

    const nodesDesc = root.descendants();
    const minX = d3.min(nodesDesc, d => d.x!)!;
    const maxX = d3.max(nodesDesc, d => d.x!)!;
    const offsetX = (width - padding.left - padding.right - (maxX - minX)) / 2 - minX;
    nodesDesc.forEach(d => { d.x = d.x! + offsetX + padding.left; d.y = d.y! + padding.top; });

    this.linkElements = this.svg.append('g')
      .selectAll<SVGLineElement, d3.HierarchyLink<GraphNode>>('line')
      .data(root.links())
      .enter()
      .append('line')
      .attr('x1', d => d.source.x!)
      .attr('y1', d => d.source.y!)
      .attr('x2', d => d.target.x!)
      .attr('y2', d => d.target.y!)
      .attr('stroke', '#9ca3af')
      .attr('stroke-width', 2)
      .attr('marker-end', 'url(#arrowhead)');

    this.nodeElements = this.svg.append('g')
      .selectAll<SVGPathElement, d3.HierarchyNode<GraphNode>>('path')
      .data(nodesDesc)
      .enter()
      .append('path')
      .attr('d', d3.symbol().type(d3.symbolCircle).size(3000))
      .attr('fill', '#60a5fa')
      .attr('stroke', '#3b82f6')
      .attr('stroke-width', 2)
      .attr('transform', d => `translate(${d.x},${d.y})`);

    this.svg.append('g')
      .selectAll<SVGTextElement, d3.HierarchyNode<GraphNode>>('text')
      .data(nodesDesc)
      .enter()
      .append('text')
      .text(d => d.data.label)
      .attr('x', d => d.x!)
      .attr('y', d => d.y! + 5)
      .attr('text-anchor', 'middle')
      .attr('fill', '#f9fafb')
      .attr('font-size', 12);
  }

  private prepareAnimation(nodes: GraphNode[], edges: GraphEdge[]) {
    const start = nodes[0]?.id;
    const adj = new Map<string, string[]>();
    edges.forEach(e => { if (!adj.has(e.from)) adj.set(e.from, []); adj.get(e.from)!.push(e.to); });
    const visited = new Set<string>();
    const order: string[] = [];
    const edgeSeq: { from: string; to: string }[] = [];
    const dfs = (u: string | undefined) => {
      if (!u || visited.has(u)) return;
      visited.add(u); order.push(u);
      const nxt = adj.get(u) || [];
      for (const v of nxt) { edgeSeq.push({ from: u, to: v }); dfs(v); }
    };
    dfs(start);
    this.nodeOrder = order;
    this.edgesOrder = edgeSeq;
    this.stepIndex = 0;
  }

  playD3() { if (!this.isPlaying) { this.isPlaying = true; this.tickD3(); } }
  pauseD3() { this.isPlaying = false; if (this.timerRef) clearTimeout(this.timerRef); }
  resetD3() {
    this.pauseD3();
    this.stepIndex = 0;
    this.nodeElements?.attr('fill', '#60a5fa').attr('stroke', '#3b82f6');
    this.linkElements?.attr('stroke', '#9ca3af').attr('stroke-width', 2);
    this.svg.selectAll('text').attr('fill', '#f9fafb');
  }

private tickD3() {
  if (!this.isPlaying) return;

  // Stop when all edges are traversed
  if (this.stepIndex >= this.edgesOrder.length) {
    this.isPlaying = false;
    return;
  }

  const e = this.edgesOrder[this.stepIndex];

  // 🔹 First highlight the source node (yellow → red)
  this.nodeElements
    .filter(d => d.data.id === e.from)
    .transition()
    .duration(this.speedMs / 3)
    .attr('fill', '#ef4444') // 🔴 active red
    .attr('stroke', '#b91c1c'); // darker red stroke

  this.svg
    .selectAll('text')
    .filter(d => (d as d3.HierarchyNode<GraphNode>).data.id === e.from)
    .transition()
    .duration(this.speedMs / 3)
    .attr('fill', '#ffffff'); // bright label

  // Highlight edge
  const edgePath = this.linkElements.filter(
    d => d.source.data.id === e.from && d.target.data.id === e.to
  );
  edgePath
    .transition()
    .duration(this.speedMs / 3)
    .attr('stroke', '#10b981') // 🟢 green path
    .attr('stroke-width', 3);

  // Animate green dot moving along edge
  const pathEl = edgePath.node() as SVGLineElement;
  if (pathEl) {
    const length = pathEl.getTotalLength();
    const dot = this.svg
      .append('circle')
      .attr('r', 4)
      .attr('fill', '#10b981')
      .attr('opacity', 1)
      .raise();

    dot
      .transition()
      .duration(this.speedMs)
      .attrTween('transform', () => t => {
        const p = pathEl.getPointAtLength(t * length);
        return `translate(${p.x},${p.y})`;
      })
      .on('end', () => {
        dot.remove();

        // 🔹 After traversal finishes, mark target node as visited
        this.nodeElements
          .filter(d => d.data.id === e.to)
          .transition()
          .duration(this.speedMs / 2)
          .attr('fill', '#ef4444') // 🔴 visited red
          .attr('stroke', '#b91c1c');

        this.svg
          .selectAll('text')
          .filter(d => (d as d3.HierarchyNode<GraphNode>).data.id === e.to)
          .transition()
          .duration(this.speedMs / 2)
          .attr('fill', '#ffffff');

        // Move to next edge
        this.stepIndex++;
        this.timerRef = setTimeout(() => this.tickD3(), this.speedMs);
      });
  }
}



  /* ----------------- AI Suggestions ----------------- */

// ⚡ Fetch + typing animation
async fetchAISuggestionsTyping() {
  if (!this.monacoEditorInstance) return;

  // ✅ Cancel any previous typing in progress
  if (this.typingInterval) {
    clearInterval(this.typingInterval);
    this.typingInterval = null;
  }

  const code = this.monacoEditorInstance.getValue();
  const payload = { language: this.selectedLang, code };

  // Reset UI state
  this.isTyping = true;
  this.displayedSuggestions = [];
  this.aiSuggestions = [];

  try {
    const res: any = await lastValueFrom(
      this.http.post<any>('http://localhost:8080/api/ai-suggest', payload)
    );

    // ✅ Get clean response text
    const fullText: string = (res?.response && res.response.trim().length > 0)
      ? res.response
      : "❌ No AI suggestions available.";

    // Split into lines
    this.aiSuggestions = fullText
                            .split(/\r?\n/)
                            .filter(line => line.trim() !== '')
                            .map(line => this.highlightLine(line));

    // 🚨 Special handling for rate limiter message
    if (fullText.includes("Please try again after")) {
  this.displayedSuggestions = [
    `<span class="text-yellow-400 font-bold">⚠️ ${fullText}</span>`
  ];
  this.isTyping = false;
  this.cdr.detectChanges();
  return;
}


    // Otherwise animate line by line
    for (const line of this.aiSuggestions) {
      await this.typeLine(line);
    }
  } catch (err) {
    console.error('AI Suggestions error:', err);
    this.aiSuggestions = ["❌ Failed to fetch AI suggestions. Please try again later."];
    this.displayedSuggestions = [...this.aiSuggestions];
  } finally {
    this.isTyping = false;
    this.cdr.detectChanges();
  }
}

typeLine(line: string): Promise<void> {
  return new Promise<void>((resolve) => {
    let i = 0;
    const plainText = line.replace(/<[^>]+>/g, ''); // strip tags
    let typed = "";

    // Extract wrapper (span with classes)
    const wrapperMatch = line.match(/^<span[^>]*>(.*)<\/span>$/);
    const wrapperStart = wrapperMatch ? line.substring(0, line.indexOf('>') + 1) : "";
    const wrapperEnd = wrapperMatch ? "</span>" : "";

    this.displayedSuggestions.push('');
    this.typingInterval = setInterval(() => {
      typed += plainText[i] || '';
      this.displayedSuggestions[this.displayedSuggestions.length - 1] =
        wrapperStart + typed + wrapperEnd; // always keep wrapper
      i++;
      this.cdr.detectChanges();

      if (i >= plainText.length) {
        clearInterval(this.typingInterval);
        this.typingInterval = null;
        setTimeout(() => resolve(), 150);
      }
    }, 30);
  });
}



highlightLine(line: string): string {
  if (line.toLowerCase().includes("output")) {
    return `<span class="text-yellow-400 font-bold">⚡ ${line}</span>`;
  } else if (line.toLowerCase().includes("bad practices")) {
    return `<span class="text-red-400 font-bold">🚨 ${line}</span>`;
  } else if (line.toLowerCase().includes("suggestions")) {
    return `<span class="text-green-400 font-bold">✅ ${line}</span>`;
  } else if (line.includes("Please try again after")) {
    return `<span class="text-yellow-400 font-bold">⚠️ ${line}</span>`;
  }
  return `<span class="text-gray-200">${line}</span>`;
}






fetchAISuggestions() {
  if (!this.monacoEditorInstance) return;
  const code = this.monacoEditorInstance.getValue();
  const payload = { language: this.selectedLang, code };

  this.http.post<any>('http://localhost:8080/api/ai-suggest', payload).subscribe({
    next: (res) => {
      const fullText: string =
        (res?.response && res.response.trim().length > 0)
          ? res.response
          : "❌ No AI suggestions available.";

      if (fullText.startsWith("⏳  Please try again after")) {
        this.aiSuggestions = [fullText];
        this.displayedSuggestions = [...this.aiSuggestions];
      } else {
        this.aiSuggestions = fullText
                            .split(/\r?\n/)
                            .filter(line => line.trim() !== '')
                            .map(line => this.highlightLine(line));

        this.displayedSuggestions = [...this.aiSuggestions];
      }

      this.cdr.detectChanges();
    },
    error: (err) => {
      console.error("AI Suggestions error:", err);
      this.aiSuggestions = ["❌ Failed to fetch AI suggestions. Please try again later."];
      this.displayedSuggestions = [...this.aiSuggestions];
      this.cdr.detectChanges();
    }
  });
}




  /* ----------------- Helpers ----------------- */
  getStrokeOffset(score: number) { const r = 45; return 2 * Math.PI * r - (score / 100) * 2 * Math.PI * r; }
  getCircumference(r: number) { return 2 * Math.PI * r; }

  copyReport(): void {
    if (!this.formattedOutput.length) return;
    const text = this.formattedOutput.map(sec => `${sec.title}\n${sec.content}`).join('\n\n');
    navigator.clipboard.writeText(text).then(() => alert('📋 Report copied!'));
  }

  highlightReport(text: string): string {
    if (!text) return '';
    text = text.replace(/⚠️ (.+)/g, `<span class="text-red-400 font-bold">⚠️ $1</span>`);
    text = text.replace(/🔹 Method: (.+)/g, `<span class="text-blue-400 font-semibold">🔹 Method: $1</span>`);
    text = text.replace(/Class: (.+)/g, `<span class="text-yellow-300 font-bold">Class: $1</span>`);
    text = text.replace(/LOC: (\d+)/g, `LOC: <span class="text-green-300 font-bold">$1</span>`);
    text = text.replace(/Cyclomatic Complexity: (\d+)/g, `Cyclomatic Complexity: <span class="text-orange-400 font-bold">$1</span>`);
    text = text.replace(/Local Variables: (\d+)/g, `Local Variables: <span class="text-purple-400 font-bold">$1</span>`);
    text = text.replace(/Max Nesting Level: (\d+)/g, `Max Nesting Level: <span class="text-pink-400 font-bold">$1</span>`);
    text = text.replace(/Total Methods: (\d+)/g, `Total Methods: <span class="text-cyan-400 font-bold">$1</span>`);
    text = text.replace(/✅ (.+)/g, `<span class="text-green-400 font-semibold">✅ $1</span>`);
    return text.replace(/\n/g, '<br>');
  }

  toArray(input: string | string[] | undefined): string[] {
    if (!input) return [];
    return Array.isArray(input) ? input : [input];
  }


fetchVivaQuestions() {
  if (!this.monacoEditorInstance) return;
  
  this.vivaLoading = true;
  this.vivaSubmitted = false;
  this.vivaQuestions = [];
  this.vivaAnswers = [];
  this.totalMarks = 0;
  this.marksPerQuestion = 0;
  this.vivaResult = ''; // clear old result

  const payload = {
    code: this.monacoEditorInstance.getValue(),
    language: this.selectedLang
  };

  this.http.post<any>('http://localhost:8000/viva', payload).subscribe({
    next: res => {
      if (res?.response) {
        // ⚠️ Show rate limit / error message directly
        this.vivaResult = `<p class="text-red-400 font-semibold">${res.response}</p>`;
        this.vivaQuestions = [];
        this.vivaAnswers = [];
        this.totalMarks = 0;
        this.marksPerQuestion = 0;
        this.vivaSubmitted = true; // so UI can show it
      } else if (res?.questions && res.questions.length > 0) {
        // ✅ Normal questions flow
        this.vivaQuestions = res.questions.map((q: any, index: number) => ({
          index: index + 1,
          question: q.question,
          options: q.options || [],
          answer: q.answer || ''
        }));

        this.totalMarks = res.marks || this.vivaQuestions.length;
        this.marksPerQuestion = this.totalMarks / this.vivaQuestions.length;
        this.vivaAnswers = new Array(this.vivaQuestions.length).fill(null);

      } else {
        console.warn('No questions received from backend.');
        this.vivaQuestions = [];
        this.vivaAnswers = [];
        this.totalMarks = 0;
        this.marksPerQuestion = 0;
      }

      this.vivaLoading = false;
      this.cdr.detectChanges();
    },
    error: err => {
      console.error('Viva fetch error:', err);
      this.vivaResult = `<p class="text-red-400 font-semibold">❌ Failed to fetch viva questions. Please try again later.</p>`;
      this.vivaQuestions = [];
      this.vivaAnswers = [];
      this.vivaLoading = false;
      this.cdr.detectChanges();
    }
  });
}




submitVivaAnswers() {
  if (!this.vivaAnswers.length) return;

  // ⚠️ Check for unanswered questions
  const unanswered = this.vivaAnswers.some(ans => ans === null || ans === '');
  if (unanswered) {
    this.vivaWarning = "⚠️ Please answer all questions before submitting.";
    this.vivaSubmitted = false;
    this.vivaLoading = false;
    this.cdr.detectChanges();
    return;
  }

  // ✅ Clear warning if everything is answered
  this.vivaWarning = '';
  this.vivaLoading = true;

  let score = 0;
  let resultHtml = '<ol class="list-decimal pl-5">';

  this.vivaQuestions.forEach((q, i) => {
    const userAnswer = this.vivaAnswers[i];
    const correct = userAnswer === q.answer;
    if (correct) score += this.marksPerQuestion;

    resultHtml += `<li class="mb-2">
      <p class="font-semibold">${q.question}</p>
      <p>Your answer: <span class="${correct ? 'text-green-400' : 'text-red-400'}">${userAnswer || 'No answer'}</span></p>
      <p>Correct answer: <span class="text-green-300">${q.answer}</span></p>
    </li>`;
  });

  resultHtml += `</ol>`;
  resultHtml += `<p class="mt-4 font-bold">Score: <span class="text-yellow-400">${score} / ${this.totalMarks}</span></p>`;

  this.vivaResult = resultHtml;
  this.vivaSubmitted = true;
  this.vivaLoading = false;
  this.cdr.detectChanges();
}




}
