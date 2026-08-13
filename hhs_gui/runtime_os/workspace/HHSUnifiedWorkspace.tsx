import React, { useEffect, useMemo, useState } from "react"
import { RuntimeOS } from "../core/RuntimeOS"
import { HHSProductWorkspace } from "./HHSProductWorkspace"

export interface HHSUnifiedWorkspaceProps {
  websocketUrl: string
}

function channelEndpoint(runtimeEndpoint: string, channel: "runtime" | "replay" | "graph" | "transport"): string {
  if (runtimeEndpoint.endsWith("/runtime")) {
    return `${runtimeEndpoint.slice(0, -"runtime".length)}${channel}`
  }
  return channel === "runtime" ? runtimeEndpoint : `/ws/${channel}`
}

/**
 * Compatibility entrypoint for the earlier unified-workspace composition.
 *
 * The previous version instantiated a second registry/router/window/workspace
 * stack with APIs that had diverged from the canonical Runtime OS. This wrapper
 * now delegates to the same product workspace used by production while keeping
 * the historical websocketUrl entry contract reusable.
 */
export const HHSUnifiedWorkspace: React.FC<HHSUnifiedWorkspaceProps> = ({ websocketUrl }) => {
  const runtimeOS = useMemo(
    () => new RuntimeOS({
      runtimeEndpoint: channelEndpoint(websocketUrl, "runtime"),
      replayEndpoint: channelEndpoint(websocketUrl, "replay"),
      graphEndpoint: channelEndpoint(websocketUrl, "graph"),
      transportEndpoint: channelEndpoint(websocketUrl, "transport"),
      diagnosticsEnabled: true,
      mobileMode: true,
    }),
    [websocketUrl],
  )

  const [transportState, setTransportState] = useState("CONNECTING")
  const [transportError, setTransportError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    runtimeOS.initialize()
      .then(() => {
        if (!mounted) return
        setTransportState(runtimeOS.getMetrics().connected ? "CONNECTED" : "ON_DEMAND")
      })
      .catch((reason: unknown) => {
        if (!mounted) return
        setTransportError(reason instanceof Error ? reason.message : String(reason))
        setTransportState("DEGRADED")
      })

    return () => {
      mounted = false
      runtimeOS.shutdown()
    }
  }, [runtimeOS])

  return (
    <HHSProductWorkspace
      runtimeOS={runtimeOS}
      transportState={transportState}
      transportError={transportError}
    />
  )
}

export default HHSUnifiedWorkspace
