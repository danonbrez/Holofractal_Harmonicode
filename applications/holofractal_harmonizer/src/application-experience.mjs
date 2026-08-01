import { initIntuitiveIDE } from './intuitive-ide.mjs';
import { initApplicationStudio } from './application-studio.mjs';
import { initIntegratedAssistant } from './integrated-assistant.mjs';

const EXPERIENCE_SCHEMA = 'HHS_APPLICATION_EXPERIENCE_BOOT_V6';
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

function reconcileApplicationProjectIdentity() {
  const pending = window.HHSPendingApplicationProjectIdentity;
  const input = document.querySelector('#ide-project-name');
  const requested = String(pending?.name || '').trim();
  if (!(input instanceof HTMLInputElement) || !requested) return false;
  input.value = requested;
  input.dataset.hhsApplicationStudioOwned = 'true';
  input.dataset.hhsIdentityCommittedAt = String(pending.requested_at || new Date().toISOString());
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  window.dispatchEvent(new CustomEvent('hhs:application-project:identity-reconciled', {
    detail: {
      schema: 'HHS_APPLICATION_PROJECT_IDENTITY_V1',
      name: requested,
      source: pending.source || 'APPLICATION_STUDIO',
      frontend_is_authority: false,
    },
  }));
  return true;
}

function enforceCriticalSurfacePostconditions() {
  window.HHSApplicationStudio?.ensurePrimaryControl?.();
  window.HHSIntegratedAssistant?.open?.();
  reconcileApplicationProjectIdentity();

  const launchers = [...document.querySelectorAll('[id="ide-new-app"]')];
  const launcher = launchers[0] || null;
  const gallery = document.querySelector('#ide-application-gallery');
  const assistantView = document.querySelector('#assistant-view');
  const assistantPrompt = document.querySelector('#prompt-input');

  if (launchers.length !== 1) {
    throw new Error(`HHS_APPLICATION_LAUNCHER_CARDINALITY_INVALID: ${launchers.length}`);
  }
  if (!(launcher instanceof HTMLButtonElement)
      || !launcher.isConnected
      || launcher.hidden
      || launcher.disabled
      || launcher.closest('[hidden]')) {
    throw new Error('HHS_APPLICATION_LAUNCHER_NOT_ACTIONABLE');
  }
  if (!gallery || !gallery.isConnected) {
    throw new Error('HHS_APPLICATION_GALLERY_NOT_MOUNTED');
  }
  if (!window.HHSIntegratedAssistant || typeof window.HHSIntegratedAssistant.open !== 'function') {
    throw new Error('HHS_INTEGRATED_ASSISTANT_NOT_INITIALIZED');
  }
  if (!assistantView || !assistantView.isConnected || assistantView.hidden) {
    throw new Error('HHS_INTEGRATED_ASSISTANT_NOT_VISIBLE');
  }
  if (!assistantPrompt || !assistantPrompt.isConnected || assistantPrompt.hidden) {
    throw new Error('HHS_INTEGRATED_ASSISTANT_PROMPT_NOT_VISIBLE');
  }

  return Object.freeze({
    public_application_launcher_count: launchers.length,
    public_application_launcher_actionable: true,
    application_gallery_mounted: true,
    integrated_assistant_visible: true,
    integrated_assistant_prompt_visible: true,
  });
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
  if (bootRecord) {
    enforceCriticalSurfacePostconditions();
    return bootRecord;
  }
  const initialized = [];
  const support = [];

  initialize('HHSIntuitiveIDE', initIntuitiveIDE, initialized);
  const legacyLauncherRetired = retireLegacyApplicationLauncher();
  initialize('HHSApplicationStudio', initApplicationStudio, initialized);
  initialize('HHSIntegratedAssistant', initIntegratedAssistant, initialized);
  const criticalSurface = enforceCriticalSurfacePostconditions();

  const supportReady = Promise.allSettled([
    loadSupport('project-lifecycle', './project-lifecycle.mjs', 'initProjectLifecycle', 'HHSProjectLifecycle', support),
    loadSupport('integrated-workbench', './integrated-workbench.mjs', 'initIntegratedWorkbench', 'HHSIntegratedWorkbench', support),
    loadSupport('deployable-app-compiler', './deployable-app-compiler.mjs', 'initDeployableAppCompiler', 'HHSDeployableAppCompiler', support),
  ]).then((results) => {
    const projectIdentityReconciled = reconcileApplicationProjectIdentity();
    enforceCriticalSurfacePostconditions();
    window.dispatchEvent(new CustomEvent('hhs:application-experience:support-settled', {
      detail: {
        schema: EXPERIENCE_SCHEMA,
        support: support.map((entry) => ({ ...entry })),
        results,
        project_identity_reconciled: projectIdentityReconciled,
      },
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
    project_identity_reconciled_after_support_hydration: true,
    ...criticalSurface,
    new_application_control: true,
    application_gallery: true,
    integrated_assistant: true,
    creates_real_runnable_projects: window.HHSApplicationStudio?.creates_real_runnable_projects === true,
    frontend_is_authority: false,
  });
  window.HHSApplicationExperience = bootRecord;
  window.dispatchEvent(new CustomEvent('hhs:application-experience:ready', { detail: bootRecord }));
  return bootRecord;
}

window.addEventListener('hhs:application-project:identity-requested', reconcileApplicationProjectIdentity);

export function startApplicationExperience() {
  if (bootRecord) {
    enforceCriticalSurfacePostconditions();
    return bootRecord;
  }
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

startApplicationExperience();
