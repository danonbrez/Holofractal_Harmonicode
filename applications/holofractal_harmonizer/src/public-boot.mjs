const BOOT_SCHEMA = 'HHS_PUBLIC_MODULE_BOOT_V2';
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

  // Pass 176 is preserved additively at /pass176-ide/. Its Visual IDE controller
  // belongs to the core public graph and must become independently available before
  // later presentation/integration projections are hydrated. This ordering does not
  // transfer VM81, Hash72, Hash216, browser, checkpoint, or persistence authority to
  // the frontend; it only prevents later projections from starving inherited IDE boot.
  const visualIDE = launch('visual-ide', './visual-ide.mjs');
  const browser = launch('browser', './browser.mjs');
  const workflowDefault = browser.then(() => launch('ux-default', './ux-default.mjs'));

  const corePublicGraph = Promise.allSettled([
    visualIDE,
    browser,
    workflowDefault,
  ]);

  const productionIntegration = corePublicGraph.then(() =>
    launch('production-integration', './production-integration.mjs'));
  const applicationExperience = corePublicGraph.then(() =>
    launch('application-experience', './application-experience.mjs'));

  const allSettled = Promise.allSettled([
    visualIDE,
    browser,
    workflowDefault,
    productionIntegration,
    applicationExperience,
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
    visualIDE,
    browser,
    workflowDefault,
    corePublicGraph,
    productionIntegration,
    applicationExperience,
    allSettled,
    status: snapshot,
    frontend_is_authority: false,
  });
  window.HHSPublicBoot = publicBoot;
  publish();
  return publicBoot;
}
