const BOOT_SCHEMA = 'HHS_PUBLIC_MODULE_BOOT_V4';
let publicBoot = null;

export function startPublicBoot() {
  if (publicBoot) return publicBoot;

  const startedAt = performance.now();
  const records = new Map();

  const elapsed = () => Math.round(performance.now() - startedAt);
  const snapshot = () => [...records.values()].map((record) => ({ ...record }));
  const publish = () => {
    window.dispatchEvent(new CustomEvent('hhs:public-boot:state', {
      detail: {
        schema: BOOT_SCHEMA,
        elapsed_ms: elapsed(),
        modules: snapshot(),
      },
    }));
  };

  const launch = (moduleId, path) => {
    records.set(moduleId, {
      module_id: moduleId,
      path,
      state: 'LOADING',
      started_ms: elapsed(),
      completed_ms: null,
      error: null,
    });
    publish();

    return import(path).then(() => {
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
  };

  const awaitGlobalPromise = async (name, result) => {
    const promise = window[name];
    if (promise && typeof promise.then === 'function') await promise;
    return result;
  };

  // The usable application and visual editor are the critical membrane. Commit
  // Pass 176 INTERACTIVE before loading browser registry and production service
  // projections, because those projections may perform substantial hashing and
  // catalog work. They remain real and ordered, but cannot monopolize the first
  // browser interaction or prevent the visual authority from becoming observable.
  const applicationExperience = launch('application-experience', './application-experience.mjs');
  const visualIDE = applicationExperience
    .then(() => launch('visual-ide', './visual-ide.mjs'))
    .then((result) => awaitGlobalPromise('HHSVisualIDEBoot', result));
  const browser = visualIDE
    .then(() => launch('browser', './browser.mjs'))
    .then((result) => awaitGlobalPromise('HHSBrowserReady', result));
  const productionIntegration = browser.then(
    () => launch('production-integration', './production-integration.mjs'),
  );
  const workflowDefault = browser.then(() => launch('ux-default', './ux-default.mjs'));

  const allSettled = Promise.allSettled([
    applicationExperience,
    visualIDE,
    browser,
    productionIntegration,
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

  publicBoot = Object.freeze({
    schema: BOOT_SCHEMA,
    coordinator_ready: Boolean(window.HHSProductionStartupCoordinator),
    legacy_parser_module_entries_disabled: true,
    application_controls_first: true,
    visual_ide_interactive_before_browser_projection: true,
    browser_registry_before_production_projection: true,
    applicationExperience,
    browser,
    productionIntegration,
    visualIDE,
    workflowDefault,
    allSettled,
    status: snapshot,
    frontend_is_authority: false,
  });
  window.HHSPublicBoot = publicBoot;
  publish();
  return publicBoot;
}