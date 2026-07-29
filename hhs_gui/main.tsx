import React from "react"
import ReactDOM from "react-dom/client"
import { CanonicalRuntimeIDE } from "./runtime_os/core/CanonicalRuntimeIDE"
import { RuntimeOS } from "./runtime_os/core/RuntimeOS"
import "./src/styles/global.css"

declare global {
  interface Window {
    __HHS_RUNTIME_OS__?: RuntimeOS
    __HHS_REPORT_BOOT_ERROR__?: (label: string, value: unknown) => void
  }
}

type FatalBoundaryState = {
  error: Error | null
}

class FatalBoundary extends React.Component<React.PropsWithChildren, FatalBoundaryState> {
  public state: FatalBoundaryState = { error: null }

  public static getDerivedStateFromError(error: Error): FatalBoundaryState {
    return { error }
  }

  public componentDidCatch(error: Error, info: React.ErrorInfo): void {
    console.error("[HHS Runtime OS] canonical IDE failure", error, info)
    document.documentElement.dataset.hhsMounted = "error"
    document.getElementById("runtime_boot_overlay")?.remove()
  }

  public render(): React.ReactNode {
    if (!this.state.error) return this.props.children
    return (
      <main className="min-h-screen bg-neutral-950 p-6 text-white">
        <section className="mx-auto max-w-3xl rounded-2xl border border-red-900 bg-neutral-900 p-5">
          <h1 className="text-lg font-semibold text-red-200">HHS Visual Runtime OS could not render</h1>
          <p className="mt-2 text-sm text-neutral-300">The canonical IDE stopped on a frontend exception. The error remains visible instead of collapsing to a black page.</p>
          <pre className="mt-4 max-h-96 overflow-auto whitespace-pre-wrap rounded-lg bg-black p-3 text-xs text-red-200">{this.state.error.stack ?? this.state.error.message}</pre>
          <button className="runtime-button mt-4 px-3 py-2 text-sm" type="button" onClick={() => window.location.reload()}>
            Reload canonical IDE
          </button>
        </section>
      </main>
    )
  }
}

const rootDocument = document.documentElement
rootDocument.dataset.hhsEntry = "loaded"

try {
  const runtimeOS = new RuntimeOS({
    runtimeEndpoint: "/ws/runtime",
    replayEndpoint: "/ws/replay",
    graphEndpoint: "/ws/graph",
    transportEndpoint: "/ws/transport",
    diagnosticsEnabled: true,
    mobileMode: window.matchMedia("(max-width: 900px)").matches,
  })

  const rootElement = document.getElementById("root")
  if (!rootElement) throw new Error("Missing #root application mount")

  ReactDOM.createRoot(rootElement).render(
    <FatalBoundary>
      <CanonicalRuntimeIDE runtimeOS={runtimeOS} />
    </FatalBoundary>,
  )

  window.__HHS_RUNTIME_OS__ = runtimeOS

  if (import.meta.hot) {
    import.meta.hot.dispose(() => runtimeOS.destroy())
  }
} catch (error: unknown) {
  rootDocument.dataset.hhsEntry = "failed"
  window.__HHS_REPORT_BOOT_ERROR__?.("frontend_react_entry_error", error)
  throw error
}
