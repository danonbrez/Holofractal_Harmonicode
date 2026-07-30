import React, { useEffect } from "react"
import { HHSWorkspaceShell } from "../workspace/HHSWorkspaceShell"
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
    <div data-testid="hhs-canonical-runtime-ide" className="min-h-screen bg-neutral-950 text-white">
      <HHSWorkspaceShell
        runtimeOS={runtimeClient as unknown as RuntimeOS}
        transportState="ON_DEMAND"
      />
    </div>
  )
}
