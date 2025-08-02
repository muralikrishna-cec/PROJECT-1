import { Component, ElementRef, Input, AfterViewInit, ViewChild, OnDestroy } from '@angular/core';
import * as monaco from 'monaco-editor';

@Component({
  selector: 'app-monaco-editor',
  template: `<div #editorContainer class="monaco-editor" style="height: 400px;"></div>`,
  standalone: true
})
export class MonacoEditorComponent implements AfterViewInit, OnDestroy {
  @ViewChild('editorContainer', { static: true }) editorContainer!: ElementRef;
  @Input() code: string = '';
  @Input() language: string = 'javascript';

  private editorInstance!: monaco.editor.IStandaloneCodeEditor;

  ngAfterViewInit(): void {
    this.editorInstance = monaco.editor.create(this.editorContainer.nativeElement, {
      value: this.code,
      language: this.language,
      theme: 'vs-dark',
      automaticLayout: true
    });
  }

  ngOnDestroy(): void {
    this.editorInstance?.dispose();
  }

  getCode(): string {
    return this.editorInstance.getValue();
  }
}
