import React, { useEffect, useMemo, useState } from "react"
import { RuntimeOS } from "./RuntimeOS"
import { RuntimeWindow } from "./RuntimeWindowManager"
import { RuntimeWindowContent } from "./RuntimeWindowContent"

export interface RuntimeDesktopProps {
  runtimeOS: RuntimeOS
}

export const RuntimeDesktop: React.FC<RuntimeDesktopProps> = ({ runtimeOS }) => {
  const [windows, setWindows] = useState<RuntimeWindow[]>([])
  const [metrics, setMetrics] = useState(runtimeOS.getMetrics())

  useEffect(() => {
    let mounted = true
    const refresh = (): void => {
      if (!mounted) return
      setWindows(runtimeOS.windowManager.getWindows())
      setMetrics(runtimeOS.getMetrics())
    }
    refresh()
    const interval = window.setInterval(refresh, 250)
    return () => {
      mounted = false
      window.clearInterval(interval)
    }
  }, [runtimeOS])

  const sortedWindows = useMemo(
    () => [...windows].sort((a, b) => Number(Boolean(b.focused)) - Number(Boolean(a.focused))),
    [windows],
  )

  return (
    <div className="fixed inset-0 overflow-hidden bg-black text-white">
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: "radial-gradient(circle at center, rgba(34,211,238,0.10), transparent 70%)",
        }}
      />
      <div
        className="absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage:
            "linear-gradient(to right, white 1px, transparent 1px), linear-gradient(to bottom, white 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />

      <div className="absolute right-4 top-4 z-[9999] flex flex-col gap-1 rounded-xl border border-cyan-950 bg-black/70 px-4 py-3 font-mono text-[10px] backdrop-blur-md">
        <div className="text-cyan-300">RuntimeOS</div>
        <div className="text-neutral-500">runtimeEvents: {metrics.sockets.totalEvents}</div>
        <div className="text-neutral-500">windows: {metrics.windows.windows}</div>
        <div className="text-neutral-500">graphNodes: {metrics.store.graphNodes}</div>
      </div>

      {sortedWindows.map((runtimeWindow) => (
        <RuntimeDesktopWindow
          key={runtimeWindow.id}
          runtimeOS={runtimeOS}
          runtimeWindow={runtimeWindow}
        />
      ))}
    </div>
  )
}

interface RuntimeDesktopWindowProps {
  runtimeOS: RuntimeOS
  runtimeWindow: RuntimeWindow
}

const RuntimeDesktopWindow: React.FC<RuntimeDesktopWindowProps> = ({ runtimeOS, runtimeWindow }) => {
  if (runtimeWindow.minimized) return null

  return (
    <div
      className={`absolute overflow-hidden rounded-2xl border backdrop-blur-xl transition-all ${
        runtimeWindow.focused
          ? "border-cyan-500/40 shadow-[0_0_50px_rgba(34,211,238,0.18)]"
          : "border-neutral-800"
      }`}
      style={{
        left: runtimeWindow.x,
        top: runtimeWindow.y,
        width: runtimeWindow.width,
        height: runtimeWindow.height,
        background: "rgba(0,0,0,0.82)",
      }}
      onMouseDown={() => runtimeOS.windowManager.focusWindow(runtimeWindow.id)}
    >
      <div className="flex h-12 items-center justify-between border-b border-neutral-800 bg-black/70 px-4 backdrop-blur-md">
        <div className="flex flex-col">
          <div className="text-sm font-semibold text-cyan-300">{runtimeWindow.title}</div>
          <div className="font-mono text-[10px] text-neutral-500">{runtimeWindow.applicationId}</div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            aria-label={`Minimize ${runtimeWindow.title}`}
            onClick={() => runtimeOS.windowManager.minimizeWindow(runtimeWindow.id)}
            className="h-3 w-3 rounded-full bg-yellow-500"
          />
          <button
            type="button"
            aria-label={`Maximize ${runtimeWindow.title}`}
            onClick={() => runtimeOS.windowManager.maximizeWindow(runtimeWindow.id)}
            className="h-3 w-3 rounded-full bg-green-500"
          />
          <button
            type="button"
            aria-label={`Close ${runtimeWindow.title}`}
            onClick={() => runtimeOS.windowManager.closeWindow(runtimeWindow.id)}
            className="h-3 w-3 rounded-full bg-red-500"
          />
        </div>
      </div>
      <div className="absolute inset-x-0 bottom-0 top-12 overflow-hidden">
        <RuntimeWindowContent runtimeOS={runtimeOS} applicationId={runtimeWindow.applicationId} />
      </div>
    </div>
  )
}

export default RuntimeDesktop
