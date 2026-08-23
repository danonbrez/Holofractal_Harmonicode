import { initIntuitiveIDE } from './intuitive-ide.mjs';
import { initApplicationStudio } from './application-studio.mjs';

const SCHEMA = 'HHS_APPLICATION_CRITICAL_PATH_V1';

function ensureControl(globalName, selector, initializer, initialized) {
  const reused = Boolean(window[globalName] && document.querySelector(selector));
  if (!reused) initializer();
  if (!window[globalName] || !document.querySelector(selector)) {
    throw new Error(`HHS_APPLICATION_CRITICAL_CONTROL_MISSING: ${globalName} ${selector}`);
  }
  initialized.push(Object.freeze({
    component: globalName,
    selector,
    state: reused ? 'REUSED' : 'READY',
  }));
}

const initialized = [];
ensureControl('HHSIntuitiveIDE', '#ide-new-app', initIntuitiveIDE, initialized);
ensureControl('HHSApplicationStudio', '#ide-application-gallery', initApplicationStudio, initialized);

const criticalPath = Object.freeze({
  schema: SCHEMA,
  state: 'INTERACTIVE_CONTROLS_READY',
  initialized: Object.freeze(initialized),
  new_application_control: true,
  application_gallery: true,
  creates_real_runnable_projects: window.HHSApplicationStudio.creates_real_runnable_projects === true,
  frontend_is_authority: false,
});

window.HHSApplicationCriticalPath = criticalPath;
window.dispatchEvent(new CustomEvent('hhs:application-critical-path:ready', { detail: criticalPath }));

export default criticalPath;
