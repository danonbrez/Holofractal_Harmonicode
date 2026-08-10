import React, { useEffect, useState } from "react"
import { RuntimeOS } from "./RuntimeOS"
import { HHSProductWorkspace } from "../workspace/HHSProductWorkspace"

export interface RuntimeShellProps {
  runtimeOS: RuntimeOS
}

/**
 * Compatibility entrypoint for earlier Runtime OS boot paths.
 *
 * The product workspace is now the single UI composition authority. RuntimeOS
 * remains a frontend orchestration/projection client only; backend runtime and
 * pass surfaces remain authoritative.
 */
export const RuntimeShell: React.FC<RuntimeShellProps> = ({ runtimeOS }) => {
  const [booted, setBooted] = useState(false)
  const [bootError, setBootError] = useState<string | null>(null)
  const [transportState, setTransportState] = useState("CONNECTING")

  useEffect(() => {
    let mounted = true

    runtimeOS.initialize()
      .then(() => {
        if (!mounted) return
        setBooted(true)
        setTransportState(runtimeOS.getMetrics().connected ? "CONNECTED" : "ON_DEMAND")
      })
      .catch((reason: unknown) => {
        if (!mounted) return
        setBootError(reason instanceof Error ? reason.message : String(reason))
        setTransportState("DEGRADED")
        setBooted(true)
      })

    return () => {
      mounted = false
      runtimeOS.shutdown()
    }
  }, [runtimeOS])

  if (!booted) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-neutral-950 p-6 text-cyan-200">
        <div className="rounded-xl border border-cyan-950 bg-black/60 px-5 py-4 font-mono text-sm">
          Initializing HHS Visual Runtime OS…
        </div>
      </main>
    )
  }

  return (
    <HHSProductWorkspace
      runtimeOS={runtimeOS}
      transportState={transportState}
      transportError={bootError}
    />
  )
}

export default RuntimeShell
