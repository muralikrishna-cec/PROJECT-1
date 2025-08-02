// Force Monaco to use workers correctly
self.MonacoEnvironment = {
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
