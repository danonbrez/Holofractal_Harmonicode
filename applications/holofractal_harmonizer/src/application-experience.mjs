import { initProjectLifecycle } from './project-lifecycle.mjs';
import { initIntegratedWorkbench } from './integrated-workbench.mjs';
import { initIntuitiveIDE } from './intuitive-ide.mjs';
import { initApplicationStudio } from './application-studio.mjs';
import { initDeployableAppCompiler } from './deployable-app-compiler.mjs';

const EXPERIENCE_SCHEMA = 'HHS_APPLICATION_EXPERIENCE_BOOT_V1';
let bootRecord = null;

function initialize(globalName, initializer, initialized) {
  if (window[globalName]) {
    initialized.push({ component: globalName, state: 'REUSED' });
    return;
  }
  initializer();
  if (!window[globalName]) throw new Error(`HHS_APPLICATION_EXPERIENCE_MISSING: ${globalName}`);
  initialized.push({ component: globalName, state: 'READY' });
}

export function startApplicationExperience() {
  if (bootRecord) return bootRecord;
  const initialized = [];

  initialize('HHSProjectLifecycle', initProjectLifecycle, initialized);
  initialize('HHSIntegratedWorkbench', initIntegratedWorkbench, initialized);
  initialize('HHSIntuitiveIDE', initIntuitiveIDE, initialized);
  initialize('HHSApplicationStudio', initApplicationStudio, initialized);
  initialize('HHSDeployableAppCompiler', initDeployableAppCompiler, initialized);

  bootRecord = Object.freeze({
    schema: EXPERIENCE_SCHEMA,
    state: 'READY',
    initialized: Object.freeze(initialized.map((entry) => Object.freeze({ ...entry }))),
    new_application_control: Boolean(document.querySelector('#ide-new-app')),
    application_gallery: Boolean(document.querySelector('#ide-application-gallery')),
    creates_real_runnable_projects: window.HHSApplicationStudio?.creates_real_runnable_projects === true,
    frontend_is_authority: false,
  });
  window.HHSApplicationExperience = bootRecord;
  window.dispatchEvent(new CustomEvent('hhs:application-experience:ready', { detail: bootRecord }));
  return bootRecord;
}

startApplicationExperience();
