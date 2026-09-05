import { pass185BootCoordinator } from "./runtime_os/core/Pass185BootCoordinator"

declare global {
  interface Window {
    __HHS_REPORT_BOOT_ERROR__?: (label: string, value: unknown) => void
  }
}

const root = document.documentElement
root.dataset.hhsBootstrap = "loaded"

const report = (label: string, value: unknown): void => {
  const reporter = window.__HHS_REPORT_BOOT_ERROR__
  if (reporter) {
    reporter(label, value)
    return
  }
  console.error(`[HHS Runtime OS] ${label}`, value)
}

void import("./main")
  .then(() => {
    root.dataset.hhsBootstrap = "import-complete"
    pass185BootCoordinator.markCoreModulesReady("canonical IDE module graph imported")
  })
  .catch((error: unknown) => {
    root.dataset.hhsBootstrap = "import-failed"
    pass185BootCoordinator.fail("frontend_canonical_module_import_error", String(error))
    report("frontend_canonical_module_import_error", error)
  })

export {}
