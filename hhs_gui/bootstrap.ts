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
  })
  .catch((error: unknown) => {
    root.dataset.hhsBootstrap = "import-failed"
    report("frontend_canonical_module_import_error", error)
  })

export {}
