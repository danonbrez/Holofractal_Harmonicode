import { createBuiltinModuleRegistry, materializeModules } from './module-library.mjs';
import { hash216Identity } from './hash216-browser.mjs';
import { createPass177WorkflowRegistry } from './workflow-engine.mjs';

const TEMPLATE_ID = /^[a-z0-9]+(?:[.-][a-z0-9]+)*$/;
const lines = (...values) => `${values.join('\n')}\n`;

function slugify(value) {
  const slug = String(value || 'application').normalize('NFKD').toLowerCase()
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 64);
  return slug || 'application';
}

function safePath(value) {
  const path = String(value || '').replaceAll('\\', '/').replace(/^\.\//, '');
  if (!path || path.startsWith('/') || path.split('/').includes('..')) throw new TypeError(`unsafe project path: ${value}`);
  return path;
}

function render(content, variables) {
  return String(content).replace(/\{\{([A-Za-z][A-Za-z0-9_]*)\}\}/g, (_, key) => String(variables[key] ?? ''));
}

function normalizeTemplate(input) {
  if (!input || typeof input !== 'object' || !TEMPLATE_ID.test(input.id || '')) throw new TypeError(`invalid template id: ${input?.id}`);
  if (!Array.isArray(input.files) || input.files.length === 0) throw new TypeError(`template ${input.id} requires files`);
  return Object.freeze({
    schema: 'hhs.pass177.template/v1',
    id: input.id,
    version: input.version || '1.0.0',
    label: input.label || input.id,
    description: input.description || '',
    family: input.family || 'application',
    target: input.target || 'web',
    entrypoint: safePath(input.entrypoint),
    workflowId: input.workflowId || 'web.application.source-zip',
    modules: Object.freeze([...(input.modules || [])]),
    tests: Object.freeze([...(input.tests || [])]),
    files: Object.freeze(input.files.map((file) => Object.freeze({
      path: safePath(file.path),
      mediaType: file.mediaType || 'text/plain',
      content: String(file.content),
    }))),
  });
}

const BASE_STYLE = lines(
  ':root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }',
  '* { box-sizing: border-box; }',
  'body { margin: 0; min-height: 100vh; background: radial-gradient(circle at 50% -15%, #43301d, #15100c 58%); color: #f5ead8; }',
  'button, input, select, textarea { font: inherit; }',
  'button { border: 1px solid #896537; border-radius: 10px; background: #3c2a16; color: #f7d68f; padding: .7rem 1rem; cursor: pointer; }',
  '.shell { width: min(1080px, calc(100% - 24px)); margin: auto; padding: 24px 0 48px; }',
  '.panel { border: 1px solid #60482f; border-radius: 18px; background: rgba(34, 26, 19, .96); box-shadow: 0 24px 80px #0008; overflow: hidden; }',
  '.bar { display: flex; gap: 12px; align-items: center; justify-content: space-between; padding: 16px 18px; border-bottom: 1px solid #60482f; }',
  '.body { padding: 18px; }',
  '.grid { display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }',
  '.card { padding: 16px; border: 1px solid #5b432c; border-radius: 14px; background: #211912; }',
  '.muted { color: #b7a58d; }',
  '@media (max-width: 640px) { .bar { align-items: flex-start; flex-direction: column; } .body { padding: 12px; } }',
);

const WEB_SHELL_HTML = lines(
  '<!doctype html>',
  '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
  '<title>{{projectName}}</title><link rel="stylesheet" href="./style.css"><link rel="stylesheet" href="./src/modules/accessible-controls.css"></head>',
  '<body><main class="shell"><section class="panel"><header class="bar"><div><small class="muted">PASS 177 PROJECT</small><h1>{{projectName}}</h1></div><button id="action">Run workflow</button></header>',
  '<div class="body"><p>This application was assembled from registered modules and remains editable after export.</p><output id="status" aria-live="polite">Ready.</output></div></section></main><script type="module" src="./app.js"></script></body></html>',
);

const WEB_SHELL_JS = lines(
  "import { createLocalJsonStore } from './src/modules/local-json.mjs';",
  "const store = createLocalJsonStore('{{projectSlug}}:state');",
  "const status = document.querySelector('#status');",
  "document.querySelector('#action').addEventListener('click', () => { const count = (store.read({ count: 0 }).count || 0) + 1; store.write({ count }); status.textContent = 'Workflow action completed ' + count + ' time(s).'; });",
);

const DASHBOARD_HTML = lines(
  '<!doctype html>',
  '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
  '<title>{{projectName}}</title><link rel="stylesheet" href="./style.css"><link rel="stylesheet" href="./src/modules/accessible-controls.css"></head>',
  '<body><main class="shell"><section class="panel"><header class="bar"><div><small class="muted">DATA APPLICATION</small><h1>{{projectName}}</h1></div><label>CSV file <input id="file" type="file" accept=".csv,text/csv"></label></header>',
  '<div class="body"><div id="summary" class="grid"></div><div class="card" style="margin-top:14px;overflow:auto"><table id="table"></table></div></div></section></main><script type="module" src="./app.js"></script></body></html>',
);

const DASHBOARD_JS = lines(
  "import { parseCsv } from './src/modules/csv.mjs';",
  "const file = document.querySelector('#file'); const summary = document.querySelector('#summary'); const table = document.querySelector('#table');",
  "function render(rows) { const width = Math.max(0, ...rows.map((row) => row.length)); summary.innerHTML = '<div class=\"card\"><b>' + Math.max(0, rows.length - 1) + '</b><div class=\"muted\">data rows</div></div><div class=\"card\"><b>' + width + '</b><div class=\"muted\">columns</div></div>'; table.innerHTML = rows.slice(0, 100).map((row, index) => '<tr>' + row.map((cell) => (index ? '<td>' : '<th>') + String(cell).replaceAll('&','&amp;').replaceAll('<','&lt;') + (index ? '</td>' : '</th>')).join('') + '</tr>').join(''); }",
  "file.addEventListener('change', async () => { const [source] = file.files || []; if (source) render(parseCsv(await source.text())); });",
  "render([['Name','Value'],['Alpha','72'],['Beta','81'],['Gamma','64']]);",
);

const CANVAS_HTML = lines(
  '<!doctype html>',
  '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{projectName}}</title><link rel="stylesheet" href="./style.css"></head>',
  '<body><main class="shell"><section class="panel"><header class="bar"><div><small class="muted">CANVAS SIMULATION</small><h1>{{projectName}}</h1></div><button id="reset">Reset</button></header><div class="body"><canvas id="scene" width="960" height="540" aria-label="Interactive simulation"></canvas></div></section></main><script type="module" src="./app.js"></script></body></html>',
);

const CANVAS_JS = lines(
  "import { startFixedStepLoop } from './src/modules/fixed-step-loop.mjs';",
  "const canvas = document.querySelector('#scene'); const context = canvas.getContext('2d'); let x = 120; let velocity = 150;",
  "function reset() { x = 120; velocity = 150; } document.querySelector('#reset').addEventListener('click', reset);",
  "startFixedStepLoop({ update(stepMs) { x += velocity * stepMs / 1000; if (x < 24 || x > canvas.width - 24) velocity *= -1; }, render() { context.fillStyle = '#0d0a08'; context.fillRect(0,0,canvas.width,canvas.height); context.fillStyle = '#e2a849'; context.beginPath(); context.arc(x, canvas.height / 2, 22, 0, Math.PI * 2); context.fill(); } });",
);

const MEDIA_HTML = lines(
  '<!doctype html>',
  '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{projectName}}</title><link rel="stylesheet" href="./style.css"></head>',
  '<body><main class="shell"><section class="panel"><header class="bar"><div><small class="muted">LOCAL MEDIA WORKFLOW</small><h1>{{projectName}}</h1></div></header><div class="body grid">',
  '<section class="card"><h2>Audio</h2><input id="audioFile" type="file" accept="audio/*"><audio id="audio" controls></audio></section>',
  '<section class="card"><h2>Video</h2><input id="videoFile" type="file" accept="video/*"><video id="video" controls style="width:100%"></video></section>',
  '</div></section></main><script type="module" src="./app.js"></script></body></html>',
);

const MEDIA_JS = lines(
  "import { bindAudioFile } from './src/modules/audio-player.mjs';",
  "import { bindVideoFile } from './src/modules/video-player.mjs';",
  "bindAudioFile(document.querySelector('#audioFile'), document.querySelector('#audio'));",
  "bindVideoFile(document.querySelector('#videoFile'), document.querySelector('#video'));",
);

const NODE_API_SERVER = lines(
  "import { createServer } from 'node:http';",
  "const port = Number(process.env.PORT || 3000);",
  "const server = createServer((request, response) => { response.setHeader('content-type', 'application/json'); if (request.url === '/health') { response.end(JSON.stringify({ ok: true, service: '{{projectSlug}}' })); return; } response.statusCode = 404; response.end(JSON.stringify({ error: 'not_found' })); });",
  "server.listen(port, () => console.log('{{projectName}} listening on ' + port));",
);

const CLI_SOURCE = lines(
  '#!/usr/bin/env node',
  "const [command = 'help', ...args] = process.argv.slice(2);",
  "if (command === 'echo') console.log(args.join(' ')); else if (command === 'version') console.log('0.1.0'); else console.log('Commands: echo <text>, version');",
);

const templates = [
  normalizeTemplate({
    id: 'modular-web-application', label: 'Modular Web Application', family: 'web-application', target: 'web', entrypoint: 'index.html',
    description: 'Accessible web shell with local persistence, tests, and independent source ZIP export.',
    modules: ['ui.accessible-controls', 'storage.local-json', 'test.browser-smoke', 'package.source-zip'], tests: ['node tests/smoke.mjs'],
    files: [
      { path: 'index.html', mediaType: 'text/html', content: WEB_SHELL_HTML },
      { path: 'style.css', mediaType: 'text/css', content: BASE_STYLE },
      { path: 'app.js', mediaType: 'text/javascript', content: WEB_SHELL_JS },
    ],
  }),
  normalizeTemplate({
    id: 'offline-pwa', label: 'Offline Progressive Web App', family: 'progressive-web-application', target: 'pwa', entrypoint: 'index.html', workflowId: 'pwa.application.source-zip',
    description: 'Installable offline web application with deterministic cache files.',
    modules: ['ui.accessible-controls', 'storage.local-json', 'pwa.offline', 'test.browser-smoke', 'package.source-zip'], tests: ['node tests/smoke.mjs'],
    files: [
      { path: 'index.html', mediaType: 'text/html', content: WEB_SHELL_HTML.replace('</head>', '<link rel="manifest" href="./manifest.webmanifest"></head>').replace('</body>', '<script>if (\'serviceWorker\' in navigator) navigator.serviceWorker.register(\'./service-worker.js\');</script></body>') },
      { path: 'style.css', mediaType: 'text/css', content: BASE_STYLE },
      { path: 'app.js', mediaType: 'text/javascript', content: WEB_SHELL_JS },
    ],
  }),
  normalizeTemplate({
    id: 'csv-data-explorer', label: 'CSV Data Explorer', family: 'dashboard', target: 'web', entrypoint: 'index.html',
    description: 'Local-first CSV ingestion, summary metrics, and tabular preview.',
    modules: ['ui.accessible-controls', 'data.csv', 'test.browser-smoke', 'package.source-zip'], tests: ['node tests/smoke.mjs'],
    files: [
      { path: 'index.html', mediaType: 'text/html', content: DASHBOARD_HTML },
      { path: 'style.css', mediaType: 'text/css', content: `${BASE_STYLE}table { width: 100%; border-collapse: collapse; } th, td { padding: .65rem; border-bottom: 1px solid #4e3b28; text-align: left; }\n` },
      { path: 'app.js', mediaType: 'text/javascript', content: DASHBOARD_JS },
    ],
  }),
  normalizeTemplate({
    id: 'canvas-simulation', label: 'Canvas Simulation', family: 'game-and-simulation', target: 'web', entrypoint: 'index.html',
    description: 'Fixed-step simulation loop with a runnable Canvas 2D surface.',
    modules: ['game.fixed-step-loop', 'graphics.canvas2d', 'test.browser-smoke', 'package.source-zip'], tests: ['node tests/smoke.mjs'],
    files: [
      { path: 'index.html', mediaType: 'text/html', content: CANVAS_HTML },
      { path: 'style.css', mediaType: 'text/css', content: `${BASE_STYLE}canvas { width: 100%; aspect-ratio: 16/9; background: #0d0a08; border: 1px solid #6d5130; border-radius: 14px; }\n` },
      { path: 'app.js', mediaType: 'text/javascript', content: CANVAS_JS },
    ],
  }),
  normalizeTemplate({
    id: 'local-media-studio', label: 'Local Media Studio', family: 'multimodal-media', target: 'web', entrypoint: 'index.html',
    description: 'Local audio and video loading with safe object-URL cleanup.',
    modules: ['media.audio-player', 'media.video-player', 'test.browser-smoke', 'package.source-zip'], tests: ['node tests/smoke.mjs'],
    files: [
      { path: 'index.html', mediaType: 'text/html', content: MEDIA_HTML },
      { path: 'style.css', mediaType: 'text/css', content: `${BASE_STYLE}audio, video, input { width: 100%; margin-top: 12px; }\n` },
      { path: 'app.js', mediaType: 'text/javascript', content: MEDIA_JS },
    ],
  }),
  normalizeTemplate({
    id: 'node-rest-service', label: 'Node REST Service', family: 'service', target: 'node', entrypoint: 'src/server.mjs', workflowId: 'node.service.source-zip',
    description: 'Dependency-free Node HTTP service with a health route.',
    modules: ['test.node-smoke', 'package.source-zip'], tests: ['node --test'],
    files: [
      { path: 'src/server.mjs', mediaType: 'text/javascript', content: NODE_API_SERVER },
      { path: 'test/server.test.mjs', mediaType: 'text/javascript', content: lines("import test from 'node:test';", "import assert from 'node:assert/strict';", "test('service source exposes health', async () => { const source = await (await import('node:fs/promises')).readFile(new URL('../src/server.mjs', import.meta.url), 'utf8'); assert.match(source, /\\/health/); });") },
    ],
  }),
  normalizeTemplate({
    id: 'node-cli-tool', label: 'Node CLI Tool', family: 'command-line', target: 'node', entrypoint: 'src/cli.mjs', workflowId: 'node.service.source-zip',
    description: 'Dependency-free command-line application with deterministic commands.',
    modules: ['test.node-smoke', 'package.source-zip'], tests: ['node --test'],
    files: [
      { path: 'src/cli.mjs', mediaType: 'text/javascript', content: CLI_SOURCE },
      { path: 'test/cli.test.mjs', mediaType: 'text/javascript', content: lines("import test from 'node:test';", "import assert from 'node:assert/strict';", "import { spawnSync } from 'node:child_process';", "test('echo command', () => { const run = spawnSync(process.execPath, ['src/cli.mjs', 'echo', 'hello'], { encoding: 'utf8' }); assert.equal(run.status, 0); assert.equal(run.stdout.trim(), 'hello'); });") },
    ],
  }),
];

export const PASS177_TEMPLATES = Object.freeze(templates);

export class TemplateRegistry {
  #templates = new Map();

  constructor(values = PASS177_TEMPLATES) {
    for (const value of values) this.register(value);
  }

  register(value) {
    const template = normalizeTemplate(value);
    if (this.#templates.has(template.id)) throw new Error(`template already registered: ${template.id}`);
    this.#templates.set(template.id, template);
    return template;
  }

  get(id) {
    const template = this.#templates.get(id);
    if (!template) throw new Error(`unknown template: ${id}`);
    return template;
  }

  list({ family, target, capability } = {}) {
    const modules = createBuiltinModuleRegistry();
    return [...this.#templates.values()].filter((template) => (
      (!family || template.family === family)
      && (!target || template.target === target)
      && (!capability || template.modules.some((id) => modules.get(id).capabilities.includes(capability)))
    ));
  }
}

function mergeFiles(templateFiles, moduleFiles, variables) {
  const files = new Map();
  for (const source of [...templateFiles, ...moduleFiles]) {
    const file = { path: safePath(source.path), mediaType: source.mediaType || 'text/plain', content: render(source.content, variables) };
    if (files.has(file.path)) throw new Error(`project file collision at ${file.path}`);
    files.set(file.path, file);
  }
  return [...files.values()].sort((left, right) => left.path.localeCompare(right.path));
}

function generatedPackageJson(template, variables) {
  const scripts = template.target === 'node'
    ? { start: `node ${template.entrypoint}`, test: 'node --test' }
    : { test: 'node tests/smoke.mjs' };
  return `${JSON.stringify({ name: variables.projectSlug, version: '0.1.0', private: true, type: 'module', scripts }, null, 2)}\n`;
}

export async function createPass177Project({ templateId, name, modules = [], variables = {}, previousRoot, sequence = 0 }, dependencies = {}) {
  const templateRegistry = dependencies.templateRegistry || new TemplateRegistry();
  const moduleRegistry = dependencies.moduleRegistry || createBuiltinModuleRegistry();
  const workflowRegistry = dependencies.workflowRegistry || createPass177WorkflowRegistry();
  const template = templateRegistry.get(templateId);
  workflowRegistry.get(template.workflowId);
  const projectName = String(name || template.label).trim() || template.label;
  const projectSlug = slugify(projectName);
  const values = { projectName, projectSlug, ...variables };
  const moduleOutput = materializeModules(moduleRegistry, [...template.modules, ...modules], values);
  let files = mergeFiles(template.files, moduleOutput.files, values);
  if (!files.some((file) => file.path === 'package.json')) {
    files.push({ path: 'package.json', mediaType: 'application/json', content: generatedPackageJson(template, values) });
    files.sort((left, right) => left.path.localeCompare(right.path));
  }
  const manifestBase = {
    schema: 'hhs.pass177.project/v1',
    id: projectSlug,
    name: projectName,
    slug: projectSlug,
    family: template.family,
    target: template.target,
    template: { id: template.id, version: template.version },
    entrypoint: template.entrypoint,
    workflow: { id: template.workflowId, version: workflowRegistry.get(template.workflowId).version },
    modules: moduleOutput.modules.map((module) => ({ id: module.id, version: module.version })),
    tests: template.tests,
    commands: moduleOutput.commands,
    permissions: [...new Set(moduleOutput.modules.flatMap((module) => module.permissions))],
    files: files.map((file) => ({ path: file.path, mediaType: file.mediaType, bytes: new TextEncoder().encode(file.content).length })),
    inheritedPasses: [174, 175, 176, 177],
  };
  const identity = await hash216Identity({ manifest: manifestBase, files: files.map(({ path, mediaType, content }) => ({ path, mediaType, content })) }, { previousRoot, sequence });
  const manifest = { ...manifestBase, identity: { algorithm: identity.algorithm, root: identity.root, payloadSha256: identity.payloadSha256, previousRoot: identity.previousRoot, sequence: identity.sequence, vm81EchoRequired: true } };
  files.push({ path: 'hhs.project.json', mediaType: 'application/json', content: `${JSON.stringify(manifest, null, 2)}\n` });
  files.sort((left, right) => left.path.localeCompare(right.path));
  return Object.freeze({
    schema: 'hhs.pass177.generated-project/v1',
    manifest: Object.freeze(manifest),
    identity,
    files: Object.freeze(files.map((file) => Object.freeze({ ...file, dirty: false, checkpoint: `Generated from ${template.label} v${template.version}` }))),
  });
}

function materializeIdeTemplate(template) {
  const moduleRegistry = createBuiltinModuleRegistry();
  const variables = { projectName: template.label, projectSlug: slugify(template.label) };
  const moduleOutput = materializeModules(moduleRegistry, template.modules, variables);
  const files = mergeFiles(template.files, moduleOutput.files, variables);
  return Object.freeze({
    id: template.id,
    label: template.label,
    description: template.description,
    entrypoint: template.entrypoint,
    files: Object.freeze(files.map((file) => Object.freeze([file.path, file.mediaType, file.content]))),
  });
}

export const PASS177_IDE_TEMPLATE_SOURCES = Object.freeze(Object.fromEntries(
  PASS177_TEMPLATES.filter((template) => ['web', 'pwa'].includes(template.target))
    .map((template) => [template.id, materializeIdeTemplate(template)]),
));

export function pass177TemplateList(filters = {}) {
  return new TemplateRegistry().list(filters);
}
