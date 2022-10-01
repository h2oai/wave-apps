const baseUrl = 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.33.0/min/vs'

// UNIMPORTANT: RequireJS paths config for monaco editor.
require.config({
  paths: {
    'vs': baseUrl,
    'vs/language': `${baseUrl}/language`,
  }
})

// UNIMPORTANT: Web worker registration for monaco editor.
window.MonacoEnvironment = {
  getWorkerUrl: function (workerId, label) {
    return `data:text/javascript;charset=utf-8,${encodeURIComponent(`
      importScripts('${baseUrl}/base/worker/workerMain.js');`
    )}`
  }
}

// Load the editor javascript.
require(['vs/editor/editor.main'], async () => {
  // Render the editor into our existing div with ID "editor".
  const editor = monaco.editor.create(document.getElementById('editor'), {
    language: 'python',
  })

  // Use cmd (mac) or ctr + S to save content.
  editor.addAction({
    id: 'save-content',
    label: 'Save',
    keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS],

    // Emit q.events.editor.save event on CMD+S.
    run: editor => window.wave.emit('editor', 'save', editor.getValue())
  })

  // When the editor text changes, emit q.events.editor.change event
  // to mark dirty state.
  editor.onDidChangeModelContent(() => window.wave.emit('editor', 'change', true))
})