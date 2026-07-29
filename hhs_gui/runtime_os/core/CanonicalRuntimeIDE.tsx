import React, { useEffect, useState } from "react"
import { HHSWorkspaceShell } from "../workspace/HHSWorkspaceShell"
import { LiveRuntimeProjectionPanel } from "./LiveRuntimeProjectionPanel"
import { RuntimeCommandPanel } from "./RuntimeCommandPanel"
import { RuntimeMutationPanel } from "./RuntimeMutationPanel"
import { RuntimeOS } from "./RuntimeOS"
import { RuntimeTopbar } from "./RuntimeTopbar"

export interface CanonicalRuntimeIDEProps {
  runtimeOS: RuntimeOS
}

type TransportState = "CONNECTING" | "CONNECTED" | "PROJECTION_UNAVAILABLE" | "ERROR"

export const CanonicalRuntimeIDE: React.FC<CanonicalRuntimeIDEProps> = ({ runtimeOS }) => {
  const [transportState, setTransportState] = useState<TransportState>("CONNECTING")
  const [transportError, setTransportError] = useState<string | null>(null)

  useEffect(() => {
    document.documentElement.dataset.hhsMounted = "true"
    document.getElementById("runtime_boot_overlay")?.remove()

    let active = true
    const timeout = window.setTimeout(() => {
      if (active) setTransportState("PROJECTION_UNAVAILABLE")
    }, 5000)

    runtimeOS.initialize()
      .then(() => {
        if (!active) return
        window.clearTimeout(timeout)
        setTransportState("CONNECTED")
      })
      .catch((error: unknown) => {
        if (!active) return
        window.clearTimeout(timeout)
        setTransportState("ERROR")
        setTransportError(error instanceof Error ? error.message : String(error))
      })

    return () => {
      active = false
      window.clearTimeout(timeout)
      runtimeOS.shutdown()
    }
  }, [runtimeOS])

  return (
    <div data-testid="hhs-canonical-runtime-ide" className="min-h-screen bg-neutral-950 text-white">
      <RuntimeTopbar runtimeOS={runtimeOS} />
      <div className="min-h-screen px-2 pb-3 pt-12 lg:px-3">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-cyan-950 bg-neutral-900/80 px-3 py-2 text-[11px] font-mono">
          <div>
            <strong className="text-cyan-300">HHS Visual Runtime OS</strong>
            <span className="ml-2 text-neutral-400">canonical workspace · backend-authorized execution</span>
          </div>
          <div className="flex items-center gap-2">
            <span className={transportState === "CONNECTED" ? "text-emerald-300" : "text-amber-300"}>
              transport: {transportState}
            </span>
            {transportError ? <span className="text-red-300">{transportError}</span> : null}
          </div>
        </div>

        <div className="grid min-w-0 grid-cols-1 gap-3 2xl:grid-cols-[minmax(0,1fr)_340px]">
          <div className="min-w-0 overflow-auto">
            <HHSWorkspaceShell />
          </div>
          <aside className="grid content-start gap-3">
            <LiveRuntimeProjectionPanel runtimeOS={runtimeOS} />
            <RuntimeCommandPanel runtimeOS={runtimeOS} />
            <RuntimeMutationPanel runtimeOS={runtimeOS} />
          </aside>
        </div>
      </div>
    </div>
  )
}
