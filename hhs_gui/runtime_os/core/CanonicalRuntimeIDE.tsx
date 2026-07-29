import React, { useEffect, useState } from "react"
import { HHSWorkspaceShell } from "../workspace/HHSWorkspaceShell"
import { RuntimeOS } from "./RuntimeOS"

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
      <HHSWorkspaceShell
        runtimeOS={runtimeOS}
        transportState={transportState}
        transportError={transportError}
      />
    </div>
  )
}
