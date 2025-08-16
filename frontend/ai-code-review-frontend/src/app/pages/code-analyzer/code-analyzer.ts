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
import * as monaco from 'monaco-editor';
import * as d3 from 'd3';
import { marked } from 'marked';

interface D3Node extends GraphNode {
  x?: number; y?: number; vx?: number; vy?: number; fx?: number | null; fy?: number | null;
}
interface D3Edge extends GraphEdge { source: D3Node; target: D3Node; }

type GraphNode = { id: string; type: string; label: string };
type GraphEdge = { from: string; to: string; condition?: string };
type AnalysisResponse = {
  nodes?: GraphNode[];
  edges?: GraphEdge[];
  metrics?: { loc?: number; functions?: number; cyclomatic_complexity?: number; quality_score?: string | number };
  report?: string;
  suggestions?: string | string[];
  analysis?: string;
};

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
  activeTab: 'analysis' | 'visualization' | 'suggestions' = 'analysis';
  metrics = { loc: 0, complexity: 0, functions: 0, score: 0 };
  formattedOutput: { title: string; content: string }[] = [];
  outputRaw: AnalysisResponse | null = null;
  aiSuggestions: string[] = [];

  private monacoEditorInstance!: monaco.editor.IStandaloneCodeEditor;
  private svg!: d3.Selection<SVGSVGElement, unknown, HTMLElement, any>;
  private simulation: d3.Simulation<D3Node, D3Edge> | null = null;
  private nodeElements!: d3.Selection<SVGPathElement, D3Node, SVGGElement, unknown>;
private linkElements!: d3.Selection<SVGLineElement, D3Edge, SVGGElement, unknown>;



  private edgeLabelElements!: d3.Selection<SVGTextElement, D3Edge, SVGGElement, unknown>;

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
      this.renderAndPrepareGraph(this.outputRaw.nodes, this.outputRaw.edges);
      this.graphRendered = true;
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
    if (target && target.value && this.monacoEditorInstance) {
      this.selectedLang = target.value;
      monaco.editor.setModelLanguage(this.monacoEditorInstance.getModel()!, this.mapLangToMonaco(target.value));
    }
  }

  submitCode(): void {
    const code = this.monacoEditorInstance.getValue();
    const payload = { language: this.selectedLang, code };

    this.http.post<AnalysisResponse>('http://localhost:8080/api/analyze', payload).subscribe({
      next: (res) => {
        this.outputRaw = res;
        this.populateMetricsAndReport(res);
        this.graphRendered = false;
        this.cdr.detectChanges();
        if (res.nodes && res.edges) this.setActiveTab('visualization'); else this.setActiveTab('analysis');
      },
      error: (err) => { console.error('Backend error:', err); alert('❌ Backend connection failed.'); }
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
    const reportText = (typeof res.report === 'string' && res.report.trim()) ? res.report.trim() :
      (typeof res.analysis === 'string' && res.analysis.trim()) ? res.analysis.trim() : 'No report available.';
    this.formattedOutput = [{ title: 'Static Report', content: marked.parse(reportText) as string }];
  }

  setActiveTab(tab: 'analysis' | 'visualization' | 'suggestions') {
    this.activeTab = tab;
    this.graphRendered = false;
    this.cdr.detectChanges();
  }

  private renderAndPrepareGraph(nodes: GraphNode[], edges: GraphEdge[]) {
    this.renderD3Graph(nodes, edges);
    this.prepareAnimation(nodes, edges);
    this.resetD3();
  }

private renderD3Graph(nodes: GraphNode[], edges: GraphEdge[]) {
  const d3Nodes: D3Node[] = nodes.map(n => ({ ...n }));
  const d3Edges: D3Edge[] = edges.map(e => ({
    ...e,
    source: d3Nodes.find(n => n.id === e.from)!,
    target: d3Nodes.find(n => n.id === e.to)!
  }));

  const container = d3.select('#graph-container');
  container.selectAll('*').remove();
  const el = container.node() as HTMLElement;
  const width = el?.clientWidth || 800;
  const height = el?.clientHeight || 500;

  this.svg = container.append('svg').attr('width', width).attr('height', height);

  // Arrow markers
  this.svg.append('defs').append('marker')
    .attr('id', 'arrowhead')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 20)
    .attr('refY', 0)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill', '#cbd5e1');

  this.simulation = d3.forceSimulation<D3Node>(d3Nodes)
    .force('link', d3.forceLink<D3Node, D3Edge>(d3Edges).id(d => d.id).distance(120))
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(width / 2, height / 2));

// ---------------- Links ----------------
this.linkElements = this.svg.append('g')
  .selectAll<SVGLineElement, D3Edge>('line')
  .data(d3Edges)
  .enter()
  .append('line')
  .attr('stroke', '#cbd5e1')
  .attr('stroke-width', 2)
  .attr('marker-end', 'url(#arrowhead)');

// ---------------- Edge labels ----------------
this.edgeLabelElements = this.svg.append('g')
  .selectAll<SVGTextElement, D3Edge>('text')
  .data(d3Edges)
  .enter()
  .append('text')
  .text(d => d.condition ?? '')
  .attr('fill', '#ffffff')
  .attr('font-size', 12)
  .attr('text-anchor', 'middle');

// ---------------- Nodes ----------------
this.nodeElements = this.svg.append('g')
  .selectAll<SVGPathElement, D3Node>('path')
  .data(d3Nodes)
  .enter()
  .append('path')
  .attr('d', d => {
    if (d.type === 'decision') return d3.symbol().type(d3.symbolDiamond).size(4000)();
    else if (d.type === 'start' || d.type === 'end') return d3.symbol().type(d3.symbolCircle).size(4000)();
    else return d3.symbol().type(d3.symbolCircle).size(2500)();
  })
  .attr('fill', '#60a5fa')
  .attr('stroke', '#3b82f6')
  .attr('stroke-width', 2)
  .attr('transform', d => `translate(${d.x ?? width / 2},${d.y ?? height / 2})`);

// ---------------- Node labels ----------------
this.svg.append('g')
  .selectAll<SVGTextElement, D3Node>('text.node-label')
  .data(d3Nodes)
  .enter()
  .append('text')
  .attr('class', 'node-label')
  .text(d => d.label)
  .attr('fill', '#ffffff')
  .attr('text-anchor', 'middle')
  .attr('dy', 5)
  .attr('font-size', 12)
  .attr('x', d => d.x ?? width / 2)
  .attr('y', d => d.y ?? height / 2);

// ---------------- Tick handler ----------------
this.simulation.on('tick', () => {
  // Links
  this.linkElements
    .attr('x1', d => d.source.x!)
    .attr('y1', d => d.source.y!)
    .attr('x2', d => d.target.x!)
    .attr('y2', d => d.target.y!);

  // Nodes
  this.nodeElements
    .attr('transform', d => `translate(${d.x},${d.y})`);

  // Node labels
  this.svg.selectAll('text.node-label')
    .attr('x', (d: any) => d.x!)
    .attr('y', (d: any) => d.y!);

  // Edge labels
  this.edgeLabelElements
    .attr('x', d => (d.source.x! + d.target.x!) / 2)
    .attr('y', d => (d.source.y! + d.target.y!) / 2);
});

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

  playD3() {
    if (this.isPlaying) return;
    this.isPlaying = true;
    this.tickD3();
  }

  pauseD3() {
    this.isPlaying = false;
    if (this.timerRef) clearTimeout(this.timerRef);
  }

  resetD3() {
    this.pauseD3();
    this.stepIndex = 0;
    this.nodeElements?.attr('fill', '#60a5fa').attr('stroke', '#3b82f6');
    this.linkElements?.attr('stroke', '#cbd5e1').attr('stroke-width', 2);
    this.svg.selectAll('text').attr('fill', '#ffffff');
  }
// ================= Animation =================
private tickD3() {
  if (!this.isPlaying) return;
  const totalSteps = this.nodeOrder.length + this.edgesOrder.length;
  if (this.stepIndex >= totalSteps) { this.isPlaying = false; return; }

  if (this.stepIndex < this.nodeOrder.length) {
    // Highlight node
    const nodeId = this.nodeOrder[this.stepIndex];
    this.nodeElements.filter(d => d.id === nodeId)
      .transition().duration(this.speedMs / 2).attr('fill', '#facc15');
  } else {
    // Animate edge flow
    const edgeIdx = this.stepIndex - this.nodeOrder.length;
    const e = this.edgesOrder[edgeIdx];
    const edgePath = this.linkElements.filter(d => d.from === e.from && d.to === e.to);

    // Highlight edge
    edgePath.transition().duration(this.speedMs / 2).attr('stroke', '#f97316').attr('stroke-width', 4);

    // Animate circle along path
    const pathEl = edgePath.node() as SVGPathElement;
    if (pathEl) {
      const length = pathEl.getTotalLength();
      const dot = this.svg.append('circle')
        .attr('r', 6)
        .attr('fill', '#f97316')
        .attr('opacity', 1);

      dot.transition()
        .duration(this.speedMs)
        .attrTween('transform', () => t => {
          const p = pathEl.getPointAtLength(t * length);
          return `translate(${p.x},${p.y})`;
        })
        .on('end', () => dot.remove());
    }
  }

  this.stepIndex++;
  this.timerRef = setTimeout(() => this.tickD3(), this.speedMs);
}


fetchAISuggestions() {
  if (!this.monacoEditorInstance) return;

  const code = this.monacoEditorInstance.getValue();
  const payload = { language: this.selectedLang, code };

  this.http.post<any>('http://localhost:8080/api/ai-suggest', payload)
    .subscribe({
      next: (res) => {
        // Wrap the single string into an array
        this.aiSuggestions = res.response ? [res.response] : [];
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('AI Suggestions error:', err);
        this.aiSuggestions = ["❌ Failed to fetch AI suggestions."];
        this.cdr.detectChanges();
      }
    });
}


  getStrokeOffset(score: number) { const r = 45; return 2 * Math.PI * r - (score / 100) * 2 * Math.PI * r; }
  getCircumference(r: number) { return 2 * Math.PI * r; }

  copyReport(): void {
    if (!this.formattedOutput.length) return;
    const text = this.formattedOutput.map(sec => `${sec.title}\n${sec.content}`).join('\n\n');
    navigator.clipboard.writeText(text).then(() => alert('📋 Report copied!'));
  }
}
