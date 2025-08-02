const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

module.exports = {
  plugins: [
    new MonacoWebpackPlugin({
      languages: ['javascript', 'typescript', 'json', 'html', 'css', 'cpp', 'python']
    })
  ]
};
