import './production-startup-coordinator.mjs';

const BOOT_SCHEMA = 'HHS_PUBLIC_MODULE_BOOT_V1';
const startedAt = performance.now();
const records = new Map();

function elapsed() {
  return Math.round(performance.now() - startedAt);
}

function snapshot() {
  return [...records.values()].map((record) => ({ ...record }));
}

function publish() {
  window.dispatchEvent(new CustomEvent('hhs:public-boot:state', {
    detail: {
      schema: BOOT_SCHEMA,
      elapsed_ms: elapsed(),
      modules: snapshot(),
    },
  }));
}

function launch(moduleId, path) {
  records.set(moduleId, {
    module_id: moduleId,
    path,
    state: 'LOADING',
    started_ms: elapsed(),
    completed_ms: null,
    error: null,
  });
  publish();

  const promise = import(path).then(() => {
    const record = records.get(moduleId);
    record.state = 'READY';
    record.completed_ms = elapsed();
    publish();
    return { module_id: moduleId, state: 'READY' };
  }).catch((error) => {
    const record = records.get(moduleId);
    record.state = 'FAILED';
    record.completed_ms = elapsed();
    record.error = `${error?.name || 'Error'}: ${error?.message || String(error)}`;
    publish();
    window.dispatchEvent(new CustomEvent('hhs:public-boot:error', {
      detail: { ...record },
    }));
    console.error('HHS_PUBLIC_MODULE_BOOT_FAILED', moduleId, record.error);
    return { module_id: moduleId, state: 'FAILED', error: record.error };
  });

  return promise;
}

// Start independent authorities concurrently. The workflow enhancement is the
// only ordered edge: its module evaluation begins after the canonical browser
// module has evaluated, while browser bootstrap work continues asynchronously.
const browser = launch('browser', './browser.mjs');
const productionIntegration = launch('production-integration', './production-integration.mjs');
const visualIDE = launch('visual-ide', './visual-ide.mjs');
const workflowDefault = browser.then(() => launch('ux-default', './ux-default.mjs'));

const allSettled = Promise.allSettled([
  browser,
  productionIntegration,
  visualIDE,
  workflowDefault,
]).then((results) => {
  window.dispatchEvent(new CustomEvent('hhs:public-boot:settled', {
    detail: {
      schema: BOOT_SCHEMA,
      elapsed_ms: elapsed(),
      modules: snapshot(),
      results,
    },
  }));
  return results;
});

window.HHSPublicBoot = Object.freeze({
  schema: BOOT_SCHEMA,
  coordinator_ready: Boolean(window.HHSProductionStartupCoordinator),
  browser,
  productionIntegration,
  visualIDE,
  workflowDefault,
  allSettled,
  status: snapshot,
  frontend_is_authority: false,
});

publish();
