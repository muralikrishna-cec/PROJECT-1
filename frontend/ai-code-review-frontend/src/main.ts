// Must be at top
import './monaco-worker-config'; // ✅ Ensure this file exists

import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';

(window as any).MonacoEnvironment = {
  getWorkerUrl: function (_moduleId: string, label: string) {
    switch (label) {
      case 'json':
        return 'assets/json.worker.js';
      case 'css':
        return 'assets/css.worker.js';
      case 'html':
        return 'assets/html.worker.js';
      case 'typescript':
      case 'javascript':
        return 'assets/ts.worker.js';
      default:
        return 'assets/editor.worker.js';
    }
  }
};


bootstrapApplication(App, appConfig).catch((err) => console.error(err));
