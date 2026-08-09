import React, { useEffect } from "react"
import { HHSProductWorkspace } from "../workspace/HHSProductWorkspace"
import { FrontendTelemetryBadge } from "../workspace/FrontendTelemetryBadge"
import { IntegratedRuntimeClient } from "./IntegratedRuntimeClient"
import type { RuntimeOS } from "./RuntimeOS"

export interface CanonicalRuntimeIDEProps {
  runtimeClient: IntegratedRuntimeClient
}

export const CanonicalRuntimeIDE: React.FC<CanonicalRuntimeIDEProps> = ({ runtimeClient }) => {
  useEffect(() => {
    document.documentElement.dataset.hhsMounted = "true"
    document.getElementById("runtime_boot_overlay")?.remove()
    return () => runtimeClient.shutdown()
  }, [runtimeClient])

  return (
    <div data-testid="hhs-canonical-runtime-ide" className="relative min-h-screen bg-neutral-950 text-white">
      <HHSProductWorkspace
        runtimeOS={runtimeClient as unknown as RuntimeOS}
        transportState="ON_DEMAND"
      />
      <div className="pointer-events-none fixed bottom-3 right-3 z-[70] max-w-[calc(100vw-1.5rem)]">
        <FrontendTelemetryBadge />
      </div>
    </div>
  )
}
