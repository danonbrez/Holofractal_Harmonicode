import {
  state,
  activeFile,
  persist,
  ensureProject,
  log,
} from './visual-ide-state.mjs';
import { initPass176Stability } from './pass176-stability.mjs';

const VISUAL_BOOT_PROMISE = Symbol.for('hhs.pass176.visual-ide.boot-promise');
const bootOptions = Object.freeze({ state, activeFile, persist, ensureProject, log });

function ensureVisualBootPromise() {
  if (window[VISUAL_BOOT_PROMISE]) return window[VISUAL_BOOT_PROMISE];

  const promise = new Promise((resolve, reject) => {
    const cleanup = () => {
      window.removeEventListener('hhs:visual-ide:interactive', onInteractive);
      window.removeEventListener('hhs:visual-ide:boot-error', onBootError);
    };
    const onInteractive = (event) => {
      cleanup();
      resolve(event.detail || window.HHSPass176?.status?.() || null);
    };
    const onBootError = (event) => {
      cleanup();
      const detail = event.detail || {};
      reject(new Error(detail.message || detail.classification || 'HHS_P176_VISUAL_IDE_BOOT_FAILED'));
    };
    window.addEventListener('hhs:visual-ide:interactive', onInteractive, { once: true });
    window.addEventListener('hhs:visual-ide:boot-error', onBootError, { once: true });
  });

  // Attach a rejection observer so an early boot failure is reported through the
  // explicit event channel without becoming an unhandled promise rejection.
  void promise.catch(() => {});
  window[VISUAL_BOOT_PROMISE] = promise;
  if (!window.HHSVisualIDEBoot) window.HHSVisualIDEBoot = promise;
  return promise;
}

const visualBootPromise = ensureVisualBootPromise();
const controllerPromise = initPass176Stability(bootOptions);
void controllerPromise.catch((error) => {
  window.dispatchEvent(new CustomEvent('hhs:pass176:early-bootstrap-error', {
    detail: {
      classification: error?.classification || 'HHS_P176_EARLY_CONTROLLER_BOOT_FAILED',
      message: error?.message || String(error),
      interactive_claimed: false,
      frontend_is_authority: false,
    },
  }));
});

window.HHSPass176EarlyBootstrap = Object.freeze({
  schema: 'HHS_PASS_176_EARLY_CONTROLLER_BOOTSTRAP_V1',
  controller_requested_before_public_graph: true,
  visual_boot_promise_registered: true,
  interactive_claimed: false,
  frontend_is_authority: false,
  controller: () => controllerPromise,
  visualBoot: () => visualBootPromise,
});
