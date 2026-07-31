import { initIntuitiveIDE } from './intuitive-ide.mjs';
import { initApplicationStudio } from './application-studio.mjs';

const EXPERIENCE_SCHEMA = 'HHS_APPLICATION_EXPERIENCE_BOOT_V4';
let bootRecord = null;
let bootPromise = null;

function initialize(globalName, initializer, initialized) {
  if (window[globalName]) {
    initialized.push({ component: globalName, state: 'REUSED' });
    return;
  }
  initializer();
  if (!window[globalName]) throw new Error(`HHS_APPLICATION_EXPERIENCE_MISSING: ${globalName}`);
  initialized.push({ component: globalName, state: 'READY' });
}

function retireLegacyApplicationLauncher() {
  const legacy = document.querySelector('#ide-simple-workflow #ide-new-app');
  if (!legacy) return false;
  legacy.id = 'ide-new-project-legacy';
  legacy.dataset.hhsLegacyProjectLauncher = 'true';
  legacy.setAttribute('aria-label', 'Open the legacy starter-project dialog');
  return true;
}

function loadSupport(component, path, initializerName, globalName, support) {
  const record = { component, state: 'LOADING', error: null };
  support.push(record);
  return import(path).then((module) => {
    if (!window[globalName]) {
      const initializer = module[initializerName];
      if (typeof initializer !== 'function') {
        throw new Error(`HHS_APPLICATION_SUPPORT_INITIALIZER_MISSING: ${initializerName}`);
      }
      initializer();
    }
    if (!window[globalName]) throw new Error(`HHS_APPLICATION_SUPPORT_MISSING: ${globalName}`);
    record.state = 'READY';
    return { component, state: 'READY' };
  }).catch((error) => {
    record.state = 'FAILED';
    record.error = `${error?.name || 'Error'}: ${error?.message || String(error)}`;
    window.dispatchEvent(new CustomEvent('hhs:application-experience:support-error', {
      detail: { ...record },
    }));
    console.error('HHS_APPLICATION_EXPERIENCE_SUPPORT_FAILED', component, record.error);
    return { component, state: 'FAILED', error: record.error };
  });
}

function initializeApplicationExperience() {
  if (bootRecord) return bootRecord;
  const initialized = [];
  const support = [];

  // The critical user path has no dependency on backend lifecycle hydration:
  // mount the inherited workflow, retire its duplicate public ID, then install
  // the single authoritative executable application launcher and gallery.
  initialize('HHSIntuitiveIDE', initIntuitiveIDE, initialized);
  const legacyLauncherRetired = retireLegacyApplicationLauncher();
  initialize('HHSApplicationStudio', initApplicationStudio, initialized);

  // Preview, source ZIP, and deployable compilation remain real, but hydrate in
  // parallel after the primary control is already usable.
  const supportReady = Promise.allSettled([
    loadSupport('project-lifecycle', './project-lifecycle.mjs', 'initProjectLifecycle', 'HHSProjectLifecycle', support),
    loadSupport('integrated-workbench', './integrated-workbench.mjs', 'initIntegratedWorkbench', 'HHSIntegratedWorkbench', support),
    loadSupport('deployable-app-compiler', './deployable-app-compiler.mjs', 'initDeployableAppCompiler', 'HHSDeployableAppCompiler', support),
  ]).then((results) => {
    window.dispatchEvent(new CustomEvent('hhs:application-experience:support-settled', {
      detail: { schema: EXPERIENCE_SCHEMA, support: support.map((entry) => ({ ...entry })), results },
    }));
    return results;
  });

  bootRecord = Object.freeze({
    schema: EXPERIENCE_SCHEMA,
    state: 'INTERACTIVE',
    initialized: Object.freeze(initialized.map((entry) => Object.freeze({ ...entry }))),
    support,
    supportReady,
    legacy_application_launcher_retired: legacyLauncherRetired,
    public_application_launcher_count: document.querySelectorAll('[id="ide-new-app"]').length,
    new_application_control: Boolean(document.querySelector('#ide-new-app')),
    application_gallery: Boolean(document.querySelector('#ide-application-gallery')),
    creates_real_runnable_projects: window.HHSApplicationStudio?.creates_real_runnable_projects === true,
    frontend_is_authority: false,
  });
  window.HHSApplicationExperience = bootRecord;
  window.dispatchEvent(new CustomEvent('hhs:application-experience:ready', { detail: bootRecord }));
  return bootRecord;
}

export function startApplicationExperience() {
  if (bootRecord) return bootRecord;
  if (document.readyState === 'loading' || !document.querySelector('#ide-view')) {
    if (!bootPromise) {
      bootPromise = new Promise((resolve, reject) => {
        const start = () => {
          try {
            resolve(initializeApplicationExperience());
          } catch (error) {
            reject(error);
          }
        };
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', start, { once: true });
        } else {
          queueMicrotask(start);
        }
      });
    }
    return bootPromise;
  }
  return initializeApplicationExperience();
}

// Safe under classic, defer, async, or dynamically injected module ordering.
// When the module is evaluated before the static IDE DOM is available, startup
// is retained and replayed exactly once at DOMContentLoaded.
startApplicationExperience();
