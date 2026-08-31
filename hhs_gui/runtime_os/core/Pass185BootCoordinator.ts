export const PASS185_BOOT_SEQUENCE = [
  "DOCUMENT_RECEIVED",
  "STATIC_ASSETS_LOADING",
  "CORE_MODULES_READY",
  "DOM_READY",
  "WORKSPACE_BOUND",
  "EDITOR_READY",
  "PREVIEW_READY",
  "INTERACTIVE",
] as const

export type Pass185BootState =
  | typeof PASS185_BOOT_SEQUENCE[number]
  | "DEGRADED_INTERACTIVE"
  | "FAILED"

export type Pass185BootHistoryEntry = {
  state: Pass185BootState
  elapsed_ms: number
  detail: string
}

export type Pass185BootSnapshot = {
  schema: "HHS_PASS185_PRODUCTION_BOOT_COORDINATOR_V1"
  state: Pass185BootState
  terminal: boolean
  deadline_ms: number
  history: Pass185BootHistoryEntry[]
  failure: { label: string; detail: string } | null
  frontend_runtime_authority: false
  canonical_runtime_authority_changed: false
}

type BootFacts = {
  staticAssetsLoading: boolean
  coreModulesReady: boolean
  domReady: boolean
  workspaceBound: boolean
  editorReady: boolean
  previewReady: boolean
  interactive: boolean
  degraded: boolean
}

declare global {
  interface Window {
    __HHS_BOOT_COORDINATOR__?: Pass185BootCoordinator
  }
}

export class Pass185BootCoordinator {
  private readonly started = performance.now()
  private readonly deadlineMs = 12000
  private state: Pass185BootState = "DOCUMENT_RECEIVED"
  private failure: { label: string; detail: string } | null = null
  private history: Pass185BootHistoryEntry[] = []
  private facts: BootFacts = {
    staticAssetsLoading: false,
    coreModulesReady: false,
    domReady: false,
    workspaceBound: false,
    editorReady: false,
    previewReady: false,
    interactive: false,
    degraded: false,
  }

  public constructor() {
    this.record("DOCUMENT_RECEIVED", "production document received")
    this.markStaticAssetsLoading("bootstrap module requested")
    if (document.readyState === "loading") {
      document.addEventListener(
        "DOMContentLoaded",
        () => this.markDomReady("DOMContentLoaded observed"),
        { once: true },
      )
    } else {
      this.markDomReady("document already ready when coordinator initialized")
    }
  }

  public markStaticAssetsLoading(detail = "static assets loading"): void {
    this.facts.staticAssetsLoading = true
    this.flush(detail)
  }

  public markCoreModulesReady(detail = "core modules ready"): void {
    this.facts.coreModulesReady = true
    this.flush(detail)
  }

  public markDomReady(detail = "DOM ready"): void {
    this.facts.domReady = true
    this.flush(detail)
  }

  public markWorkspaceBound(detail = "workspace bound"): void {
    this.facts.workspaceBound = true
    this.flush(detail)
  }

  public markEditorReady(detail = "editor capability ready"): void {
    this.facts.editorReady = true
    this.flush(detail)
  }

  public markPreviewReady(detail = "preview capability ready"): void {
    this.facts.previewReady = true
    this.flush(detail)
  }

  public markInteractive(degraded = false, detail = "interactive"): void {
    this.facts.interactive = true
    this.facts.degraded = degraded
    this.flush(detail)
  }

  public fail(label: string, value: unknown): void {
    if (this.isTerminal()) return
    const detail = typeof value === "string" ? value : String(value)
    this.failure = { label, detail }
    this.state = "FAILED"
    this.record("FAILED", label + ": " + detail)
  }

  public snapshot(): Pass185BootSnapshot {
    return {
      schema: "HHS_PASS185_PRODUCTION_BOOT_COORDINATOR_V1",
      state: this.state,
      terminal: this.isTerminal(),
      deadline_ms: this.deadlineMs,
      history: this.history.map((entry) => ({ ...entry })),
      failure: this.failure ? { ...this.failure } : null,
      frontend_runtime_authority: false,
      canonical_runtime_authority_changed: false,
    }
  }

  private isTerminal(): boolean {
    return (
      this.state === "INTERACTIVE"
      || this.state === "DEGRADED_INTERACTIVE"
      || this.state === "FAILED"
    )
  }

  private flush(detail: string): void {
    if (this.isTerminal()) return

    if (this.state === "DOCUMENT_RECEIVED" && this.facts.staticAssetsLoading) {
      this.transition("STATIC_ASSETS_LOADING", detail)
    }
    if (this.state === "STATIC_ASSETS_LOADING" && this.facts.coreModulesReady) {
      this.transition("CORE_MODULES_READY", "canonical module graph ready")
    }
    if (this.state === "CORE_MODULES_READY" && this.facts.domReady) {
      this.transition("DOM_READY", "DOMContentLoaded bounded")
    }
    if (this.state === "DOM_READY" && this.facts.workspaceBound) {
      this.transition("WORKSPACE_BOUND", "React product workspace committed")
    }
    if (this.state === "WORKSPACE_BOUND" && this.facts.editorReady) {
      this.transition("EDITOR_READY", "editor capability modules bound")
    }
    if (this.state === "EDITOR_READY" && this.facts.previewReady) {
      this.transition("PREVIEW_READY", "preview capability modules bound")
    }
    if (this.state === "PREVIEW_READY" && this.facts.interactive) {
      this.transition(
        this.facts.degraded ? "DEGRADED_INTERACTIVE" : "INTERACTIVE",
        detail,
      )
    }
  }

  private transition(next: Pass185BootState, detail: string): void {
    this.state = next
    this.record(next, detail)
  }

  private record(state: Pass185BootState, detail: string): void {
    const elapsed = Math.max(0, Math.round((performance.now() - this.started) * 1000) / 1000)
    this.history.push({ state, elapsed_ms: elapsed, detail })
    document.documentElement.dataset.hhsBootState = state
    document.documentElement.dataset.hhsBootTerminal = this.isTerminal() ? "true" : "false"
    const status = document.getElementById("runtime_boot_status")
    if (status && state !== "INTERACTIVE" && state !== "DEGRADED_INTERACTIVE") {
      status.textContent =
        "boot_state: " + state
        + "\nphase: " + String(this.history.length)
        + "\nelapsed_ms: " + String(elapsed)
    }
    window.dispatchEvent(
      new CustomEvent("hhs-pass185-boot-state", {
        detail: this.snapshot(),
      }),
    )
  }
}

export const pass185BootCoordinator =
  window.__HHS_BOOT_COORDINATOR__ ?? new Pass185BootCoordinator()

window.__HHS_BOOT_COORDINATOR__ = pass185BootCoordinator
