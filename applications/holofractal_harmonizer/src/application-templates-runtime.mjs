import { APPLICATION_TEMPLATES as BASE_TEMPLATES } from './application-templates.mjs';

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

function normalizeTemplate(template) {
  return Object.freeze({
    ...template,
    files: Object.freeze(template.files.map(([path, mediaType, content]) => Object.freeze([
      path,
      mediaType,
      template.id === 'calculator' && path.endsWith('/app.js') ? CALCULATOR_APPLICATION_SOURCE : content,
    ]))),
  });
}

export const APPLICATION_TEMPLATES = Object.freeze(Object.fromEntries(
  Object.entries(BASE_TEMPLATES).map(([id, template]) => [id, normalizeTemplate(template)]),
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
