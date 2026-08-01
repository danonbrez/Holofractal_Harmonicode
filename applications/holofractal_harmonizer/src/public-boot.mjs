const BOOT_SCHEMA = 'HHS_PUBLIC_MODULE_BOOT_V3';
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

  const launch = (moduleId, path, activate = null) => {
    records.set(moduleId, {
      module_id: moduleId,
      path,
      state: 'LOADING',
      started_ms: elapsed(),
      completed_ms: null,
      error: null,
    });
    publish();

    return import(path).then(async (module) => {
      if (typeof activate === 'function') await activate(module);
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

  // The application experience is the user-critical prerequisite. Importing
  // its module is not sufficient: await its real DOM initialization before
  // lower browser, registry, and visual IDE hydration can mutate the surface.
  const applicationExperience = launch(
    'application-experience',
    './application-experience.mjs',
    async (module) => {
      const result = await module.startApplicationExperience();
      if (!result || result.state !== 'INTERACTIVE') {
        throw new Error('HHS_APPLICATION_EXPERIENCE_NOT_INTERACTIVE');
      }
    },
  );

  const browser = applicationExperience.then((result) => {
    if (result.state !== 'READY') return result;
    return launch('browser', './browser.mjs');
  });
  const productionIntegration = applicationExperience.then((result) => {
    if (result.state !== 'READY') return result;
    return launch('production-integration', './production-integration.mjs');
  });
  const visualIDE = applicationExperience.then((result) => {
    if (result.state !== 'READY') return result;
    return launch('visual-ide', './visual-ide.mjs');
  });
  const workflowDefault = browser.then((result) => {
    if (result.state !== 'READY') return result;
    return launch('ux-default', './ux-default.mjs');
  });

  const allSettled = Promise.allSettled([
    applicationExperience,
    browser,
    productionIntegration,
    visualIDE,
    workflowDefault,
  ]).then(async (results) => {
    const experienceModule = await import('./application-experience.mjs');
    await experienceModule.startApplicationExperience();
    window.dispatchEvent(new CustomEvent('hhs:public-boot:settled', {
      detail: {
        schema: BOOT_SCHEMA,
        elapsed_ms: elapsed(),
        modules: snapshot(),
        results,
      },
    }));
    return results;
  }).catch((error) => {
    const detail = {
      schema: BOOT_SCHEMA,
      elapsed_ms: elapsed(),
      error: `${error?.name || 'Error'}: ${error?.message || String(error)}`,
      modules: snapshot(),
    };
    window.dispatchEvent(new CustomEvent('hhs:public-boot:error', { detail }));
    console.error('HHS_PUBLIC_BOOT_POSTCONDITION_FAILED', detail);
    throw error;
  });

  publicBoot = Object.freeze({
    schema: BOOT_SCHEMA,
    coordinator_ready: Boolean(window.HHSProductionStartupCoordinator),
    legacy_parser_module_entries_disabled: true,
    application_experience_awaited_before_hydration: true,
    critical_surface_reasserted_after_settlement: true,
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
