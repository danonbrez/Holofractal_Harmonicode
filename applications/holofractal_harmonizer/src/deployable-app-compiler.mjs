import { $, state, activeFile, base64ToBytes, log, setText } from './visual-ide-state.mjs';
import { createStoredZip } from './project-zip.mjs';

const encoder = new TextEncoder();

function normalizePath(path) {
  const output = [];
  for (const part of String(path || '').replaceAll('\\', '/').split('/')) {
    if (!part || part === '.') continue;
    if (part === '..') output.pop();
    else output.push(part);
  }
  return output.join('/');
}

function resolvePath(basePath, reference) {
  if (/^(?:[a-z]+:|\/\/|#|data:|blob:)/i.test(reference)) return null;
  const base = normalizePath(basePath).split('/');
  base.pop();
  return normalizePath([...base, reference].join('/'));
}

function projectFile(path) {
  const normalized = normalizePath(path);
  return state.files.find((file) => normalizePath(file.path) === normalized) || null;
}

function text(file) {
  if (!file) return '';
  if (!file.bytesB64) return file.content || '';
  return new TextDecoder().decode(base64ToBytes(file.bytesB64));
}

function bytes(file) {
  return file?.bytesB64 ? base64ToBytes(file.bytesB64) : encoder.encode(file?.content || '');
}

function mime(file) {
  const extension = String(file?.name || '').split('.').pop()?.toLowerCase();
  const map = {
    png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', webp: 'image/webp', svg: 'image/svg+xml',
    mp3: 'audio/mpeg', wav: 'audio/wav', ogg: 'audio/ogg', flac: 'audio/flac',
    mp4: 'video/mp4', webm: 'video/webm', mov: 'video/quicktime',
    pdf: 'application/pdf', json: 'application/json', txt: 'text/plain', css: 'text/css', js: 'text/javascript', mjs: 'text/javascript',
  };
  return map[extension] || 'application/octet-stream';
}

function base64(bytesValue) {
  let result = '';
  for (let offset = 0; offset < bytesValue.length; offset += 0x8000) {
    result += String.fromCharCode(...bytesValue.subarray(offset, offset + 0x8000));
  }
  return btoa(result);
}

function dataUrl(file) {
  return `data:${mime(file)};base64,${base64(bytes(file))}`;
}

function inlineCssAssets(css, cssPath) {
  return css.replace(/url\(\s*(['"]?)([^)'"\s]+)\1\s*\)/gi, (match, quote, reference) => {
    const resolved = resolvePath(cssPath, reference);
    const file = resolved ? projectFile(resolved) : null;
    return file ? `url("${dataUrl(file)}")` : match;
  });
}

function entrypoint() {
  const selected = $('#ide-preview-entrypoint')?.value || $('#ide-project-entrypoint')?.value;
  if (selected && projectFile(selected)) return selected;
  const html = state.files.find((file) => /\.html?$/i.test(file.path));
  return html?.path || null;
}

export function compileStandaloneApplication(requestedEntrypoint = entrypoint()) {
  const htmlFile = requestedEntrypoint ? projectFile(requestedEntrypoint) : null;
  if (!htmlFile || !/\.html?$/i.test(htmlFile.path)) throw new Error('BROWSER_APPLICATION_ENTRYPOINT_REQUIRED');
  let html = text(htmlFile);

  html = html.replace(/<link\b([^>]*?)href=["']([^"']+)["']([^>]*)>/gi, (match, before, reference, after) => {
    const resolved = resolvePath(htmlFile.path, reference);
    const file = resolved ? projectFile(resolved) : null;
    if (!file || !/\.css$/i.test(file.path)) return match;
    const css = inlineCssAssets(text(file), file.path).replace(/<\/style/gi, '<\\/style');
    return `<style data-hhs-compiled-source="${resolved.replaceAll('"', '&quot;')}">${css}</style>`;
  });

  html = html.replace(/<script\b([^>]*?)src=["']([^"']+)["']([^>]*)><\/script>/gi, (match, before, reference, after) => {
    const resolved = resolvePath(htmlFile.path, reference);
    const file = resolved ? projectFile(resolved) : null;
    if (!file || !/\.(?:m?js)$/i.test(file.path)) return match;
    const moduleType = /type\s*=\s*["']module["']/i.test(`${before} ${after}`) ? ' type="module"' : '';
    return `<script${moduleType} data-hhs-compiled-source="${resolved.replaceAll('"', '&quot;')}">${text(file).replace(/<\/script/gi, '<\\/script')}</script>`;
  });

  html = html.replace(/\b(src|poster)=["']([^"']+)["']/gi, (match, attribute, reference) => {
    const resolved = resolvePath(htmlFile.path, reference);
    const file = resolved ? projectFile(resolved) : null;
    return file ? `${attribute}="${dataUrl(file)}"` : match;
  });

  const marker = '<!-- Compiled by HHS Full Multimodal Application IDE: project-local code and assets inlined. -->';
  return html.includes('<!doctype') ? html.replace(/(<!doctype[^>]*>)/i, `$1\n${marker}`) : `${marker}\n${html}`;
}

export function buildDeployableApplicationZip() {
  const compiled = compileStandaloneApplication();
  const name = ($('#ide-project-name')?.value || 'hhs-application').trim();
  const slug = name.toLowerCase().replace(/[^a-z0-9._-]+/g, '-').replace(/^-+|-+$/g, '') || 'hhs-application';
  const manifest = {
    schema: 'HHS_DEPLOYABLE_BROWSER_APPLICATION_V1',
    project_name: name,
    entrypoint: 'index.html',
    source_entrypoint: entrypoint(),
    source_file_count: state.files.length,
    compiled_at: new Date().toISOString(),
    project_local_css_inlined: true,
    project_local_javascript_inlined: true,
    project_local_media_inlined: true,
    runnable_browser_application: true,
    frontend_runtime_authority: false,
  };
  const archiveBytes = createStoredZip([
    { path: 'index.html', data: compiled },
    { path: 'application.manifest.json', data: JSON.stringify(manifest, null, 2) },
    { path: 'README.txt', data: 'Open index.html in a modern browser or deploy this folder to any static web host.\n' },
  ]);
  return { archiveBytes, archiveName: `${slug}-deployable.zip`, compiled, manifest };
}

export function downloadDeployableApplication() {
  const build = buildDeployableApplicationZip();
  const url = URL.createObjectURL(new Blob([build.archiveBytes], { type: 'application/zip' }));
  const link = Object.assign(document.createElement('a'), { href: url, download: build.archiveName });
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  setText('#ide-preview-state', `DEPLOYABLE · ${build.archiveName}`);
  log(`Compiled and exported runnable browser application ${build.archiveName}.`, build.manifest);
  return build;
}

function mountCompilerAction() {
  const toolbar = document.querySelector('.ide-preview-toolbar');
  if (!toolbar || $('#ide-download-deployable-app')) return;
  const open = $('#ide-open-preview');
  const button = document.createElement('button');
  button.id = 'ide-download-deployable-app';
  button.type = 'button';
  button.textContent = 'Download App ZIP';
  button.onclick = () => {
    try { downloadDeployableApplication(); }
    catch (error) { setText('#ide-preview-state', `COMPILE FAILED · ${error.message}`); log(`Deployable application compile failed: ${error.message}`); }
  };
  toolbar.insertBefore(button, open?.nextSibling || null);
}

export function initDeployableAppCompiler() {
  mountCompilerAction();
  window.HHSDeployableAppCompiler = Object.freeze({
    compile: compileStandaloneApplication,
    buildZip: buildDeployableApplicationZip,
    download: downloadDeployableApplication,
    browser_application_is_runnable: true,
    source_and_media_are_inlined: true,
  });
  const file = activeFile();
  if (file && /\.html?$/i.test(file.path)) setText('#ide-preview-state', 'READY TO RUN');
}
