import { APPLICATION_TEMPLATES as BASE_TEMPLATES } from './application-templates.mjs';
import { HARMONIC_PUZZLE_TEMPLATE } from './harmonic-puzzle-template.mjs';
import { PLATFORMER_LEVEL1_TEMPLATE } from './platformer-template.mjs';

const CALCULATOR_APPLICATION_SOURCE = [
  'const display = document.querySelector("#display");',
  'const history = document.querySelector("#history");',
  'const keys = document.querySelector("#keys");',
  'const labels = ["C","(",")","÷","7","8","9","×","4","5","6","−","1","2","3","+","0",".","⌫","="];',
  'let expression = "";',
  'for (const label of labels) {',
  '  const button = document.createElement("button");',
  '  button.textContent = label;',
  '  button.dataset.value = label;',
  '  if ("÷×−+".includes(label)) button.dataset.kind = "operator";',
  '  keys.append(button);',
  '}',
  'function render() {',
  '  display.textContent = expression || "0";',
  '}',
  'function evaluate() {',
  '  const safe = expression.replaceAll("×", "*").replaceAll("÷", "/").replaceAll("−", "-");',
  '  if (!/^[0-9+\\-*/().\\s]+$/.test(safe)) throw new Error("Unsupported expression");',
  '  const result = Function("\\"use strict\\"; return (" + (safe || "0") + ")")();',
  '  if (!Number.isFinite(result)) throw new Error("Result is not finite");',
  '  history.textContent = expression;',
  '  expression = String(result);',
  '  render();',
  '}',
  'keys.addEventListener("click", event => {',
  '  const value = event.target.dataset.value;',
  '  if (!value) return;',
  '  try {',
  '    if (value === "C") {',
  '      expression = "";',
  '      history.textContent = "Cleared";',
  '    } else if (value === "⌫") expression = expression.slice(0, -1);',
  '    else if (value === "=") evaluate();',
  '    else expression += value;',
  '    render();',
  '  } catch (error) {',
  '    history.textContent = error.message;',
  '    expression = "";',
  '    render();',
  '  }',
  '});',
  'addEventListener("keydown", event => {',
  '  if (/^[0-9+\\-*/().]$/.test(event.key)) {',
  '    expression += event.key;',
  '    render();',
  '  }',
  '  if (event.key === "Enter") {',
  '    event.preventDefault();',
  '    keys.querySelector(\'[data-value="="]\').click();',
  '  }',
  '  if (event.key === "Backspace") {',
  '    expression = expression.slice(0, -1);',
  '    render();',
  '  }',
  '});',
].join('\n') + '\n';

const DOCUMENT_APPLICATION_SOURCE = [
  'const editor = document.querySelector("#editor");',
  'const title = document.querySelector("#title");',
  'const saved = document.querySelector("#saved");',
  'const words = document.querySelector("#words");',
  'const KEY = "hhs-document-studio-v1";',
  'function storageRead() {',
  '  try { return JSON.parse(localStorage.getItem(KEY) || "null"); }',
  '  catch { return null; }',
  '}',
  'function storageWrite(value) {',
  '  try { localStorage.setItem(KEY, JSON.stringify(value)); return true; }',
  '  catch { return false; }',
  '}',
  'const prior = storageRead();',
  'if (prior) { title.value = prior.title; editor.innerHTML = prior.html; }',
  'function count() {',
  '  const value = editor.innerText.trim();',
  '  words.textContent = `${value ? value.split(/\\s+/).length : 0} words`;',
  '}',
  'function persist() {',
  '  const stored = storageWrite({ title: title.value, html: editor.innerHTML });',
  '  saved.textContent = stored ? `Saved ${new Date().toLocaleTimeString()}` : "Session edit · autosave available after export";',
  '  count();',
  '}',
  'function download(name, type, content) {',
  '  const url = URL.createObjectURL(new Blob([content], { type }));',
  '  const link = document.createElement("a");',
  '  link.href = url;',
  '  link.download = name;',
  '  link.click();',
  '  setTimeout(() => URL.revokeObjectURL(url), 1000);',
  '}',
  'editor.addEventListener("input", persist);',
  'title.addEventListener("input", persist);',
  'document.querySelector("#saveText").onclick = () => download(`${title.value || "document"}.txt`, "text/plain", editor.innerText);',
  'document.querySelector("#saveHtml").onclick = () => download(`${title.value || "document"}.html`, "text/html", `<!doctype html><meta charset="utf-8"><title>${title.value}</title><article>${editor.innerHTML}</article>`);',
  'count();',
].join('\n') + '\n';

function normalizedContent(template, path, content) {
  if (path.endsWith('/app.js') && template.id === 'calculator') return CALCULATOR_APPLICATION_SOURCE;
  if (path.endsWith('/app.js') && template.id === 'document') return DOCUMENT_APPLICATION_SOURCE;
  return content;
}

function normalizeTemplate(template) {
  return Object.freeze({
    ...template,
    files: Object.freeze(template.files.map(([path, mediaType, content]) => Object.freeze([
      path,
      mediaType,
      normalizedContent(template, path, content),
    ]))),
  });
}

const TEMPLATE_SOURCES = Object.freeze({
  ...BASE_TEMPLATES,
  [HARMONIC_PUZZLE_TEMPLATE.id]: HARMONIC_PUZZLE_TEMPLATE,
  [PLATFORMER_LEVEL1_TEMPLATE.id]: PLATFORMER_LEVEL1_TEMPLATE,
});

export const APPLICATION_TEMPLATES = Object.freeze(Object.fromEntries(
  Object.entries(TEMPLATE_SOURCES).map(([id, template]) => [id, normalizeTemplate(template)]),
));

export function applicationTemplateList() {
  return Object.values(APPLICATION_TEMPLATES);
}

export function materializeApplicationTemplate(id) {
  const template = APPLICATION_TEMPLATES[id] || APPLICATION_TEMPLATES.web;
  return {
    ...template,
    files: template.files.map(([path, mediaType, content]) => ({
      path,
      name: path.split('/').at(-1),
      mediaType,
      content,
      dirty: true,
    })),
  };
}
