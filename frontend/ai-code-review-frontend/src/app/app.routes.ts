import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home';
import { CodeAnalyzer } from './pages/code-analyzer/code-analyzer';
import { PlagiarismCheckComponent } from './pages/plagiarism-check/plagiarism-check';
import { AiSuggestComponent } from './pages/ai-suggest/ai-suggest';
import { BatchProcessingComponent } from './pages/batch-processing/batch-processing';

export const routes: Routes = [
   { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent },
  { path: 'analyzer', component: CodeAnalyzer },
  { path: 'plagiarism', component: PlagiarismCheckComponent },
  { path: 'ai-suggest', component: AiSuggestComponent },
  {path: 'batch', component: BatchProcessingComponent},
  { path: '**', redirectTo: '/home' } // 👈 add fallback

];
