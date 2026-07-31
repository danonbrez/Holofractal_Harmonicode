const MODULE_ID = /^[a-z0-9]+(?:[.-][a-z0-9]+)*$/;
const VERSION = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/;

function freezeRecord(value) {
  if (Array.isArray(value)) return Object.freeze(value.map(freezeRecord));
  if (value && typeof value === 'object') {
    return Object.freeze(Object.fromEntries(Object.entries(value).map(([key, item]) => [key, freezeRecord(item)])));
  }
  return value;
}

function safePath(value) {
  const path = String(value || '').replaceAll('\\', '/').replace(/^\.\//, '');
  if (!path || path.startsWith('/') || path.split('/').includes('..')) {
    throw new TypeError(`unsafe module file path: ${value}`);
  }
  return path;
}

function stringArray(value, field) {
  if (value === undefined) return [];
  if (!Array.isArray(value) || value.some((item) => typeof item !== 'string' || !item.trim())) {
    throw new TypeError(`${field} must be an array of non-empty strings`);
  }
  return [...new Set(value)];
}

function normalizeFile(file) {
  if (!file || typeof file !== 'object') throw new TypeError('module files must be objects');
  if (typeof file.content !== 'string') throw new TypeError(`module file ${file.path || '<unknown>'} must contain UTF-8 text`);
  return {
    path: safePath(file.path),
    mediaType: file.mediaType || 'text/plain',
    content: file.content,
  };
}

export function normalizeModuleManifest(input) {
  if (!input || typeof input !== 'object') throw new TypeError('module manifest must be an object');
  if (!MODULE_ID.test(input.id || '')) throw new TypeError(`invalid module id: ${input.id}`);
  if (!VERSION.test(input.version || '')) throw new TypeError(`invalid semantic version: ${input.version}`);
  if (typeof input.label !== 'string' || !input.label.trim()) throw new TypeError('module label is required');
  if (typeof input.category !== 'string' || !input.category.trim()) throw new TypeError('module category is required');
  const manifest = {
    schema: 'hhs.pass177.module/v1',
    id: input.id,
    version: input.version,
    label: input.label,
    description: String(input.description || ''),
    category: input.category,
    dependencies: stringArray(input.dependencies, 'dependencies'),
    conflicts: stringArray(input.conflicts, 'conflicts'),
    capabilities: stringArray(input.capabilities, 'capabilities'),
    targets: stringArray(input.targets, 'targets'),
    permissions: stringArray(input.permissions, 'permissions'),
    contributions: {
      files: (input.contributions?.files || []).map(normalizeFile),
      workflowStages: stringArray(input.contributions?.workflowStages, 'contributions.workflowStages'),
      commands: stringArray(input.contributions?.commands, 'contributions.commands'),
    },
  };
  return freezeRecord(manifest);
}

export class ModuleRegistry {
  #modules = new Map();

  constructor(modules = []) {
    for (const module of modules) this.register(module);
  }

  register(input) {
    const manifest = normalizeModuleManifest(input);
    if (this.#modules.has(manifest.id)) throw new Error(`module already registered: ${manifest.id}`);
    this.#modules.set(manifest.id, manifest);
    return manifest;
  }

  has(id) {
    return this.#modules.has(id);
  }

  get(id) {
    const manifest = this.#modules.get(id);
    if (!manifest) throw new Error(`unknown module: ${id}`);
    return manifest;
  }

  list({ category, capability, target } = {}) {
    return [...this.#modules.values()].filter((module) => (
      (!category || module.category === category)
      && (!capability || module.capabilities.includes(capability))
      && (!target || module.targets.includes(target))
    ));
  }

  resolve(requested = []) {
    const ordered = [];
    const visiting = new Set();
    const visited = new Set();

    const visit = (id, lineage = []) => {
      if (visited.has(id)) return;
      if (visiting.has(id)) throw new Error(`module dependency cycle: ${[...lineage, id].join(' -> ')}`);
      const module = this.get(id);
      visiting.add(id);
      for (const dependency of module.dependencies) visit(dependency, [...lineage, id]);
      visiting.delete(id);
      visited.add(id);
      ordered.push(module);
    };

    for (const id of requested) visit(id);
    const selected = new Set(ordered.map((module) => module.id));
    for (const module of ordered) {
      const conflict = module.conflicts.find((id) => selected.has(id));
      if (conflict) throw new Error(`module conflict: ${module.id} conflicts with ${conflict}`);
    }
    return Object.freeze(ordered);
  }
}

function tokenValue(value) {
  return String(value ?? '');
}

function render(content, variables) {
  return content.replace(/\{\{([A-Za-z][A-Za-z0-9_]*)\}\}/g, (_, key) => tokenValue(variables[key]));
}

export function materializeModules(registry, requested, variables = {}) {
  const modules = registry.resolve(requested);
  const files = new Map();
  const workflowStages = [];
  const commands = [];
  for (const module of modules) {
    workflowStages.push(...module.contributions.workflowStages);
    commands.push(...module.contributions.commands);
    for (const source of module.contributions.files) {
      const file = {
        path: source.path,
        mediaType: source.mediaType,
        content: render(source.content, variables),
        moduleId: module.id,
      };
      const prior = files.get(file.path);
      if (prior && (prior.content !== file.content || prior.mediaType !== file.mediaType)) {
        throw new Error(`module file collision at ${file.path}: ${prior.moduleId} vs ${module.id}`);
      }
      files.set(file.path, file);
    }
  }
  return Object.freeze({
    modules,
    files: Object.freeze([...files.values()].sort((left, right) => left.path.localeCompare(right.path))),
    workflowStages: Object.freeze([...new Set(workflowStages)]),
    commands: Object.freeze([...new Set(commands)]),
  });
}

const file = (path, mediaType, content) => ({ path, mediaType, content });
const module = (value) => normalizeModuleManifest(value);

export const BUILTIN_MODULES = Object.freeze([
  module({
    id: 'ui.accessible-controls', version: '1.0.0', label: 'Accessible Controls', category: 'ui',
    description: 'Keyboard-visible, touch-safe control primitives and status announcements.',
    capabilities: ['ui', 'accessibility'], targets: ['web', 'pwa'],
    contributions: { files: [file('src/modules/accessible-controls.css', 'text/css', `:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
[aria-busy="true"] { cursor: progress; opacity: .72; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); }
`)] },
  }),
  module({
    id: 'storage.local-json', version: '1.0.0', label: 'Local JSON Storage', category: 'storage',
    description: 'Namespaced JSON persistence with schema fallback and bounded failure handling.',
    capabilities: ['persistence'], targets: ['web', 'pwa'], permissions: ['local-storage'],
    contributions: { files: [file('src/modules/local-json.mjs', 'text/javascript', `export function createLocalJsonStore(namespace) {
  const key = String(namespace);
  return {
    read(fallback = null) { try { const value = localStorage.getItem(key); return value === null ? fallback : JSON.parse(value); } catch { return fallback; } },
    write(value) { try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch { return false; } },
    clear() { try { localStorage.removeItem(key); return true; } catch { return false; } },
  };
}
`)] },
  }),
  module({
    id: 'data.csv', version: '1.0.0', label: 'CSV Data', category: 'data',
    description: 'Dependency-free CSV parsing and serialization for tabular application workflows.',
    capabilities: ['csv', 'tabular-data'], targets: ['web', 'pwa', 'node'],
    contributions: { files: [file('src/modules/csv.mjs', 'text/javascript', `export function parseCsv(text) {
  const rows = []; let row = []; let cell = ''; let quoted = false;
  for (let i = 0; i < text.length; i += 1) { const char = text[i];
    if (quoted && char === '"' && text[i + 1] === '"') { cell += '"'; i += 1; }
    else if (char === '"') quoted = !quoted;
    else if (!quoted && char === ',') { row.push(cell); cell = ''; }
    else if (!quoted && (char === '\n' || char === '\r')) { if (char === '\r' && text[i + 1] === '\n') i += 1; row.push(cell); rows.push(row); row = []; cell = ''; }
    else cell += char;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows;
}
export function stringifyCsv(rows) { return rows.map((row) => row.map((value) => { const cell = String(value ?? ''); return /[",\r\n]/.test(cell) ? '"' + cell.replaceAll('"', '""') + '"' : cell; }).join(',')).join('\n'); }
`)] },
  }),
  module({
    id: 'network.fetch-json', version: '1.0.0', label: 'Fetch JSON', category: 'network',
    description: 'Abortable JSON requests with explicit HTTP and decoding errors.',
    capabilities: ['http', 'json'], targets: ['web', 'pwa', 'node'], permissions: ['network'],
    contributions: { files: [file('src/modules/fetch-json.mjs', 'text/javascript', `export async function fetchJson(url, options = {}) {
  const response = await fetch(url, { ...options, headers: { accept: 'application/json', ...(options.headers || {}) } });
  if (!response.ok) throw new Error('HTTP ' + response.status + ' ' + response.statusText);
  try { return await response.json(); } catch (error) { throw new Error('Invalid JSON from ' + url + ': ' + error.message); }
}
`)] },
  }),
  module({
    id: 'graphics.canvas2d', version: '1.0.0', label: 'Canvas 2D Surface', category: 'graphics',
    description: 'Resolution-aware Canvas 2D setup with resize and coordinate normalization.',
    capabilities: ['canvas2d', 'graphics'], targets: ['web', 'pwa'],
    contributions: { files: [file('src/modules/canvas2d.mjs', 'text/javascript', `export function createCanvasSurface(canvas, draw) {
  const context = canvas.getContext('2d');
  function resize() { const box = canvas.getBoundingClientRect(); const ratio = Math.max(1, devicePixelRatio || 1); canvas.width = Math.round(box.width * ratio); canvas.height = Math.round(box.height * ratio); context.setTransform(ratio, 0, 0, ratio, 0, 0); draw(context, box); }
  const observer = new ResizeObserver(resize); observer.observe(canvas); resize();
  return { context, resize, dispose: () => observer.disconnect() };
}
`)] },
  }),
  module({
    id: 'game.fixed-step-loop', version: '1.0.0', label: 'Fixed-Step Game Loop', category: 'game',
    description: 'Bounded fixed-step simulation separated from rendering.',
    capabilities: ['game-loop', 'simulation'], targets: ['web', 'pwa'],
    contributions: { files: [file('src/modules/fixed-step-loop.mjs', 'text/javascript', `export function startFixedStepLoop({ update, render, stepMs = 1000 / 60, maxSteps = 5 }) {
  let active = true; let prior = performance.now(); let accumulator = 0;
  function frame(now) { if (!active) return; accumulator += Math.min(250, now - prior); prior = now; let steps = 0; while (accumulator >= stepMs && steps < maxSteps) { update(stepMs); accumulator -= stepMs; steps += 1; } render(accumulator / stepMs); requestAnimationFrame(frame); }
  requestAnimationFrame(frame); return () => { active = false; };
}
`)] },
  }),
  module({
    id: 'media.audio-player', version: '1.0.0', label: 'Audio Player', category: 'media',
    description: 'Local audio-file loading and safe object-URL lifecycle management.',
    capabilities: ['audio'], targets: ['web', 'pwa'], permissions: ['local-files'],
    contributions: { files: [file('src/modules/audio-player.mjs', 'text/javascript', `export function bindAudioFile(input, audio) { let current = null; input.addEventListener('change', () => { if (current) URL.revokeObjectURL(current); const [file] = input.files || []; if (!file) return; current = URL.createObjectURL(file); audio.src = current; audio.play().catch(() => {}); }); return () => { if (current) URL.revokeObjectURL(current); }; }
`)] },
  }),
  module({
    id: 'media.video-player', version: '1.0.0', label: 'Video Player', category: 'media',
    description: 'Local video-file loading with accessible playback controls.',
    capabilities: ['video'], targets: ['web', 'pwa'], permissions: ['local-files'],
    contributions: { files: [file('src/modules/video-player.mjs', 'text/javascript', `export function bindVideoFile(input, video) { let current = null; input.addEventListener('change', () => { if (current) URL.revokeObjectURL(current); const [file] = input.files || []; if (!file) return; current = URL.createObjectURL(file); video.src = current; video.play().catch(() => {}); }); return () => { if (current) URL.revokeObjectURL(current); }; }
`)] },
  }),
  module({
    id: 'worker.task-runner', version: '1.0.0', label: 'Task Runner', category: 'automation',
    description: 'Abortable task queue with serial execution and human-readable state.',
    capabilities: ['tasks', 'automation'], targets: ['web', 'pwa', 'node'],
    contributions: { workflowStages: ['execute-tasks'], files: [file('src/modules/task-runner.mjs', 'text/javascript', `export class TaskRunner {
  #tail = Promise.resolve();
  enqueue(label, task) { const run = async () => ({ label, value: await task() }); const next = this.#tail.then(run, run); this.#tail = next.catch(() => {}); return next; }
}
`)] },
  }),
  module({
    id: 'pwa.offline', version: '1.0.0', label: 'Offline PWA', category: 'platform',
    description: 'Installable web manifest and deterministic offline cache.',
    capabilities: ['pwa', 'offline'], targets: ['pwa'],
    contributions: { workflowStages: ['validate-pwa'], files: [
      file('manifest.webmanifest', 'application/manifest+json', `{"name":"{{projectName}}","short_name":"{{projectName}}","start_url":"./","display":"standalone","background_color":"#15100c","theme_color":"#8d6a39"}
`),
      file('service-worker.js', 'text/javascript', `const CACHE = '{{projectSlug}}-v1'; const ASSETS = ['./', './index.html', './style.css', './app.js']; self.addEventListener('install', (event) => event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)))); self.addEventListener('fetch', (event) => event.respondWith(caches.match(event.request).then((hit) => hit || fetch(event.request))));
`),
    ] },
  }),
  module({
    id: 'test.browser-smoke', version: '1.0.0', label: 'Browser Smoke Test', category: 'testing',
    description: 'Zero-dependency browser source checks suitable for generated ZIP packages.',
    capabilities: ['testing', 'browser-smoke'], targets: ['web', 'pwa'],
    contributions: { workflowStages: ['test'], commands: ['test'], files: [file('tests/smoke.mjs', 'text/javascript', `import assert from 'node:assert/strict'; import { readFile } from 'node:fs/promises';
const html = await readFile(new URL('../index.html', import.meta.url), 'utf8');
assert.match(html, /<!doctype html>/i); assert.match(html, /app\.js/); console.log('browser source smoke: PASS');
`)] },
  }),
  module({
    id: 'test.node-smoke', version: '1.0.0', label: 'Node Smoke Test', category: 'testing',
    description: 'Node built-in test harness contribution without external dependencies.',
    capabilities: ['testing', 'node'], targets: ['node'],
    contributions: { workflowStages: ['test'], commands: ['test'] },
  }),
  module({
    id: 'package.source-zip', version: '1.0.0', label: 'Source ZIP Package', category: 'packaging',
    description: 'Declares source ZIP packaging as an independent terminal workflow stage.',
    capabilities: ['zip', 'source-export'], targets: ['web', 'pwa', 'node'],
    contributions: { workflowStages: ['package-source-zip'], commands: ['export-source-zip'] },
  }),
]);

export function createBuiltinModuleRegistry() {
  return new ModuleRegistry(BUILTIN_MODULES);
}
