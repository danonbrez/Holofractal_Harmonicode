import React, { useEffect, useRef, useState } from "react"

type Json = Record<string, any>

const record = (value: unknown): Json =>
  value && typeof value === "object" ? value as Json : {}

export const Pass185TerminalPanel: React.FC = () => {
  const socketRef = useRef<WebSocket | null>(null)
  const [state, setState] = useState("CLOSED")
  const [lastMessage, setLastMessage] = useState<Json | null>(null)
  const [error, setError] = useState<string | null>(null)

  const closeTerminal = (): void => {
    const socket = socketRef.current
    socketRef.current = null
    if (socket && socket.readyState < WebSocket.CLOSING) socket.close(1000, "pass185-terminal-close")
    setState("CLOSED")
  }

  const openTerminal = (): void => {
    closeTerminal()
    setError(null)
    setState("CONNECTING")
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:"
    const socket = new WebSocket(`${protocol}//${window.location.host}/api/v1/pass175/terminal/ws/events`)
    socketRef.current = socket

    socket.addEventListener("open", () => {
      if (socketRef.current === socket) setState("OPEN")
    })
    socket.addEventListener("message", (event) => {
      if (socketRef.current !== socket) return
      try {
        const payload = record(JSON.parse(String(event.data)))
        setLastMessage(payload)
        if (payload.classification === "HHS_PASS_175_TERMINAL_WS_READY") setState("READY")
        if (payload.action === "ping" && payload.ok === true) setState("PONG")
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : String(reason))
      }
    })
    socket.addEventListener("error", () => {
      if (socketRef.current === socket) {
        setError("TERMINAL_WEBSOCKET_ERROR")
        setState("ERROR")
      }
    })
    socket.addEventListener("close", () => {
      if (socketRef.current === socket) {
        socketRef.current = null
        setState((current) => current === "ERROR" ? current : "CLOSED")
      }
    })
  }

  const ping = (): void => {
    const socket = socketRef.current
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError("TERMINAL_NOT_OPEN")
      return
    }
    socket.send(JSON.stringify({ action: "ping" }))
    setState("PING_SENT")
  }

  useEffect(() => () => {
    const socket = socketRef.current
    socketRef.current = null
    if (socket && socket.readyState < WebSocket.CLOSING) socket.close(1000, "pass185-terminal-unmount")
  }, [])

  return (
    <section data-testid="pass185-terminal-panel" className="rounded-2xl border border-neutral-800 bg-neutral-900/50 p-4">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-cyan-200">Inherited Pass 175 terminal</h2>
          <p className="mt-1 text-[10px] text-neutral-500">
            Open/close and readiness diagnostics only. Terminal authority remains backend-owned.
          </p>
        </div>
        <span data-testid="pass185-terminal-state" className="rounded-full border border-neutral-700 bg-black px-3 py-1 font-mono text-[10px] text-cyan-300">
          {state}
        </span>
      </header>

      {error ? (
        <div data-testid="pass185-terminal-error" className="mt-3 rounded-xl border border-red-900 bg-red-950/30 p-3 text-xs text-red-200">
          {error}
        </div>
      ) : null}

      <div className="mt-4 grid gap-2 sm:grid-cols-3">
        <button data-testid="pass185-terminal-open" type="button" className="runtime-button min-h-10" onClick={openTerminal}>
          Open terminal
        </button>
        <button data-testid="pass185-terminal-ping" type="button" className="runtime-button min-h-10" onClick={ping} disabled={!["OPEN", "READY", "PONG"].includes(state)}>
          Ping terminal
        </button>
        <button data-testid="pass185-terminal-close" type="button" className="runtime-button min-h-10" onClick={closeTerminal}>
          Close terminal
        </button>
      </div>

      <div className="mt-4 rounded-xl border border-neutral-800 bg-black/50 p-3">
        <div className="text-[10px] uppercase tracking-wide text-neutral-600">Last terminal message</div>
        <pre data-testid="pass185-terminal-message" className="mt-2 max-h-80 overflow-auto whitespace-pre-wrap break-all font-mono text-[10px] text-neutral-400">
          {lastMessage ? JSON.stringify(lastMessage, null, 2) : "No terminal message yet."}
        </pre>
      </div>

      <footer className="mt-3 text-[10px] text-neutral-600">
        frontend_terminal_authority=false · parallel_state_authority=false
      </footer>
    </section>
  )
}

export default Pass185TerminalPanel
