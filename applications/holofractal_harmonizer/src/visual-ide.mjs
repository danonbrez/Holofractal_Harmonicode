import './gui-reliability.mjs';
import { $, $$, state, activeFile, persist, setText, log, bytesToBase64, ensureProject, requestJson } from './visual-ide-state.mjs';
import { showIde, showOther, renderFiles, activateFile, updateLineNumbers, saveFile, createFile, addBrowserFiles, renderSnapshot, renderHash216, openBottomTab, bind3d } from './visual-ide-ui.mjs';
import { ingest, loadSnapshot, interpret, compile, run, replay, exportEgress } from './visual-ide-runtime.mjs';
import { initProjectLifecycle } from './project-lifecycle.mjs';
import { initIntegratedWorkbench } from './integrated-workbench.mjs';
import { initIntegratedAssistant } from './integrated-assistant.mjs';
import { initIntuitiveIDE } from './intuitive-ide.mjs';
import { initApplicationStudio } from './application-studio.mjs';
import { initDeployableAppCompiler } from './deployable-app-compiler.mjs';
import { initPass175Processor } from './pass175-processor.mjs';
import { initPass175TerminalProcessor } from './pass175-terminal.mjs';
import { initProductionRecovery, runBoundedProjectTest, cancelActiveJob } from './production-recovery.mjs';
import { initDeploymentHealth } from './deployment-health.mjs';
import { initPass176Stability } from './pass176-stability.mjs';

let stability = null;
const bootOptions = { state, activeFile, persist, ensureProject, log };
const bindings = new WeakMap();

function required(selector) {
  const node = $(selector);
  if (!node) throw new Error(`HHS_P176_REQUIRED_IDE_ELEMENT_MISSING: ${selector}`);
  return node;
}

function bind(node, eventName, handler, key = eventName, options = undefined) {
  if (!node) return false;
  const keys = bindings.get(node) || new Set();
  if (keys.has(key)) return false;
  node.addEventListener(eventName, handler, options);
  keys.add(key);
  bindings.set(node, keys);
  stability.own('listener', () => node.removeEventListener(eventName, handler, options), { eventName, key });
  return true;
}

function canonicalActionKey(name) {
  const value = String(name || 'action');
  const alias = value.replace(/^(workflow|command|shortcut|stage)-/, '');
  if (alias === 'index' || alias === 'snapshot') return 'snapshot';
  if (alias === 'execute') return 'run';
  if (alias === 'multimodal-ingress' || alias === 'drop-ingress') return 'ingress';
  return alias;
}

function action(name, operation, { timeoutMs = 120000, detail = name, key = canonicalActionKey(name) } = {}) {
  return (event) => {
    event?.preventDefault?.();
    void stability.runAction(name, (job) => operation(job), { timeoutMs, detail, key }).catch((error) => {
      stability.recordError(error, { action: name, recoverable: true });
    });
  };
}

async function safeInit(name, initializer, { optional = false } = {}) {
  try {
    return await Promise.resolve(initializer());
  } catch (error) {
    stability.recordError(error, { initializer: name, optional });
    if (!optional) throw error;
    return null;
  }
}

async function runGovernedLifecycle(job) {
  const abort = () => cancelActiveJob();
  if (job?.signal?.aborted) abort();
  else job?.signal?.addEventListener('abort', abort, { once: true });
  try { return await runBoundedProjectTest(); }
  finally { job?.signal?.removeEventListener?.('abort', abort); }
}

function bindCoreControls() {
  bind(required('#ide-home'), 'click', showIde, 'ide-home');
  bind(required('#assistant-home'), 'click', () => showOther('assistant'), 'assistant-home', true);
  bind(required('#object-workspace'), 'click', () => showOther('workspace'), 'object-workspace', true);
  bind(required('#return-assistant'), 'click', (event) => {
    event.stopImmediatePropagation();
    showIde();
  }, 'return-assistant', true);
  bind(required('#open-api'), 'click', (event) => {
    event.stopImmediatePropagation();
    showOther('api');
  }, 'open-api', true);
  bind(required('#assistant-open-api'), 'click', () => showOther('api'), 'assistant-open-api', true);
  for (const button of $$('[data-close-view]')) {
    bind(button, 'click', (event) => {
      event.stopImmediatePropagation();
      showIde();
    }, 'close-view', true);
  }

  const profile = required('#profile-select');
  profile.value = stability.status().profile;
  bind(profile, 'change', () => stability.setProfile(profile.value), 'performance-profile');

  bind(required('#ide-new-file'), 'click', action('file-create', () => createFile(), {
    timeoutMs: 15000,
    detail: 'Creating a project file',
  }), 'new-file');
  bind(required('#ide-save'), 'click', action('file-save', () => saveFile(), {
    timeoutMs: 30000,
    detail: 'Saving the active file',
  }), 'save-file');
  bind(required('#ide-upload-trigger'), 'click', () => required('#ide-file-input').click(), 'upload-trigger');
  bind(required('#ide-file-input'), 'change', async (event) => {
    const files = [...(event.target.files || [])];
    event.target.value = '';
    if (!files.length) return;
    await stability.runAction('multimodal-ingress', (job) => addBrowserFiles(files, () => ingest({ signal: job.signal })), {
      key: 'ingress',
      timeoutMs: 180000,
      detail: `Importing ${files.length} file${files.length === 1 ? '' : 's'}`,
    });
  }, 'file-input');

  const commands = {
    new: () => createFile(),
    save: () => saveFile(),
    ingress: (job) => ingest({ signal: job?.signal }),
    interpret: (job) => interpret({ signal: job?.signal }),
    compile: (job) => compile({ signal: job?.signal }),
    run: (job) => run({ signal: job?.signal }),
    lifecycle: (job) => runGovernedLifecycle(job),
    egress: () => exportEgress(),
  };
  const timeouts = { ingress: 180000, interpret: 120000, compile: 180000, run: 180000, lifecycle: 240000, egress: 60000 };
  for (const [selector, name] of [
    ['#ide-ingest', 'ingress'],
    ['#ide-interpret', 'interpret'],
    ['#ide-compile', 'compile'],
    ['#ide-run', 'run'],
    ['#ide-run-lifecycle', 'lifecycle'],
    ['#ide-replay', 'replay'],
    ['#ide-egress', 'egress'],
    ['#ide-download-egress', 'egress'],
  ]) {
    const operation = name === 'replay' ? (job) => replay({ signal: job?.signal }) : commands[name];
    bind(required(selector), 'click', action(`workflow-${name}`, operation, {
      timeoutMs: timeouts[name] || 120000,
      detail: `${name[0].toUpperCase()}${name.slice(1)} workflow`,
    }), `workflow-${name}`);
  }

  for (const button of $$('[data-ide-command]')) {
    const name = button.dataset.ideCommand;
    const operation = commands[name];
    if (!operation) continue;
    bind(button, 'click', action(`command-${name}`, operation, {
      timeoutMs: timeouts[name] || 120000,
      detail: `${name[0].toUpperCase()}${name.slice(1)} command`,
    }), `command-${name}`);
  }
  for (const button of $$('.ide-bottom-tabs button')) {
    bind(button, 'click', () => openBottomTab(button.dataset.bottomTab), `bottom-${button.dataset.bottomTab}`);
  }
  const stageActions = {
    ingress: (job) => ingest({ signal: job?.signal }),
    index: (job) => loadSnapshot(undefined, { signal: job?.signal }),
    snapshot: (job) => loadSnapshot(undefined, { signal: job?.signal }),
    interpret: (job) => interpret({ signal: job?.signal }),
    compile: (job) => compile({ signal: job?.signal }),
    execute: (job) => run({ signal: job?.signal }),
    egress: () => exportEgress(),
  };
  for (const button of $$('[data-stage]')) {
    const stage = button.dataset.stage;
    const operation = stageActions[stage];
    if (!operation) continue;
    bind(button, 'click', action(`stage-${stage}`, operation, {
      timeoutMs: timeouts[stage] || 180000,
      detail: `${stage[0].toUpperCase()}${stage.slice(1)} stage`,
    }), `stage-${stage}`);
  }

  const editor = required('#ide-source-editor');
  bind(editor, 'input', () => {
    const file = activeFile();
    if (file && !file.bytesB64) {
      file.content = editor.value;
      file.dirty = true;
      persist();
      renderFiles();
    }
    updateLineNumbers();
  }, 'editor-input');
  for (const eventName of ['click', 'keyup', 'select']) {
    bind(editor, eventName, updateLineNumbers, `editor-${eventName}`);
  }
  bind(window, 'hhs:pass176:recovery-applied', () => {
    renderFiles();
    const restoredPath = state.activePath || state.files[0]?.path || null;
    if (restoredPath) activateFile(restoredPath);
  }, 'pass176-recovery-render');

  const zone = required('#ide-drop-zone');
  for (const eventName of ['dragenter', 'dragover']) {
    bind(zone, eventName, (event) => {
      event.preventDefault();
      if (event.dataTransfer) event.dataTransfer.dropEffect = 'copy';
      zone.classList.add('drag-active');
    }, `drop-${eventName}`);
  }
  for (const eventName of ['dragleave', 'drop', 'dragend']) {
    bind(zone, eventName, (event) => {
      event.preventDefault();
      zone.classList.remove('drag-active');
    }, `drop-${eventName}`);
  }
  bind(zone, 'drop', (event) => {
    const files = [...(event.dataTransfer?.files || [])];
    if (!files.length) return;
    void stability.runAction('drop-ingress', (job) => addBrowserFiles(files, () => ingest({ signal: job.signal })), {
      key: 'ingress',
      timeoutMs: 180000,
      detail: `Importing ${files.length} dropped file${files.length === 1 ? '' : 's'}`,
    }).catch((error) => stability.recordError(error, { action: 'drop-ingress' }));
  }, 'drop-files');

  bind(document, 'keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
      event.preventDefault();
      action('shortcut-save', () => saveFile(), { timeoutMs: 30000, detail: 'Saving the active file' })(event);
    }
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      event.preventDefault();
      action('shortcut-lifecycle', (job) => runGovernedLifecycle(job), { timeoutMs: 240000, detail: 'Running the application lifecycle' })(event);
    }
  }, 'global-shortcuts');

  const layout = required('#ide-layout');
  if (!layout.dataset.mobilePane) layout.dataset.mobilePane = 'editor';
  for (const button of $$('.ide-mobile-dock button')) {
    bind(button, 'click', () => {
      $$('.ide-mobile-dock button').forEach((item) => item.classList.toggle('active', item === button));
      if (button.dataset.mobilePane === 'explorer') $('#registry-nav')?.classList.add('open');
      else layout.dataset.mobilePane = button.dataset.mobilePane || 'editor';
    }, `mobile-pane-${button.dataset.mobilePane || button.textContent}`);
  }
}

async function bootVisualIDE() {
  stability = await initPass176Stability(bootOptions);
  return stability.boot([
    {
      stage: 'STATIC_THEME_READY',
      run: () => {
        document.documentElement.dataset.hhsFrozenVisualBaseline = 'PASS176';
        return { theme: 'accepted-production-theme-preserved' };
      },
    },
    {
      stage: 'CORE_WORKSPACE_READY',
      run: () => bindCoreControls(),
    },
    {
      stage: 'PROJECT_STATE_RESTORED',
      run: () => {
        if (!stability.status().recoveryAvailable) stability.flushRecovery('boot-baseline');
        return { recoveryAvailable: stability.status().recoveryAvailable };
      },
    },
    {
      stage: 'EDITOR_READY',
      run: () => {
        renderFiles();
        activateFile(state.activePath);
        renderSnapshot({ projection_b64: bytesToBase64(new Uint8Array(648)), projection_hash72: 'GENESIS' });
        renderHash216({ ingestion_operation_hash216: 'GENESIS', ingestion_positions_hash216: [] });
        bind3d();
        showIde();
      },
    },
    {
      stage: 'PREVIEW_READY',
      run: async () => {
        await safeInit('project-lifecycle', initProjectLifecycle);
        await safeInit('production-recovery', initProductionRecovery);
        required('#ide-run-lifecycle').onclick = null;
        await safeInit('deployment-health', initDeploymentHealth, { optional: true });
        await safeInit('application-studio', initApplicationStudio);
        await safeInit('deployable-app-compiler', initDeployableAppCompiler);
      },
    },
    {
      stage: 'ASSISTANT_READY',
      run: () => safeInit('integrated-assistant', initIntegratedAssistant, { optional: true }),
      optional: true,
    },
    {
      stage: 'BACKEND_CAPABILITY_CHECKED',
      run: async () => {
        const [productHealth, pass175] = await Promise.all([
          requestJson('/api/product/health', { timeoutMs: 10000, retryCount: 1 }),
          requestJson('/api/v1/pass175/status', { timeoutMs: 10000, retryCount: 1 }),
        ]);
        const authorityEvidence = stability.setAuthorityEvidence({ productHealth, pass175 });
        if (!authorityEvidence.vm81AuthorityPreserved || authorityEvidence.hash72CommitStreams !== 1) {
          throw new Error('HHS_P176_BACKEND_AUTHORITY_EVIDENCE_REJECTED');
        }
        void stability.runAction('workspace-authority-bind', async ({ signal }) => {
          const projectId = await ensureProject({ signal });
          log(`Workspace authority bound to ${projectId}.`);
          return projectId;
        }, { key: 'workspace-authority-bind', timeoutMs: 30000, detail: 'Checking backend workspace authority' }).catch((error) => {
          log(`Workspace initialization deferred: ${error.message}`);
        });
        return authorityEvidence;
      },
      optional: true,
    },
    {
      stage: 'OPTIONAL_REGISTRY_HISTORY_DIAGNOSTICS_LOADING',
      run: () => {
        queueMicrotask(() => {
          void safeInit('integrated-workbench', initIntegratedWorkbench, { optional: true });
          void safeInit('intuitive-ide', initIntuitiveIDE, { optional: true });
          void safeInit('pass175-processor', initPass175Processor, { optional: true });
          void safeInit('pass175-terminal-processor', initPass175TerminalProcessor, { optional: true });
        });
        return { deferred: true };
      },
      optional: true,
    },
    {
      stage: 'INTERACTIVE',
      run: () => {
        setText('#ide-registry-state', 'LIVE');
        window.HHSVisualIDE = Object.freeze({
          state,
          show: showIde,
          ingest,
          snapshot: loadSnapshot,
          interpret,
          compile,
          run,
          lifecycle: runBoundedProjectTest,
          replay,
          egress: exportEgress,
          stability: () => stability.status(),
        });
        window.dispatchEvent(new CustomEvent('hhs:visual-ide:interactive', { detail: stability.status() }));
      },
    },
  ]);
}

const visualIdeBootPromise = bootVisualIDE();
window.HHSVisualIDEBoot = visualIdeBootPromise;
void visualIdeBootPromise.catch((error) => {
  const detail = {
    classification: error?.classification || 'HHS_P176_VISUAL_IDE_BOOT_FAILED',
    message: error?.message || String(error),
  };
  window.dispatchEvent(new CustomEvent('hhs:visual-ide:boot-error', { detail }));
  console.error(detail.classification, detail.message);
});
