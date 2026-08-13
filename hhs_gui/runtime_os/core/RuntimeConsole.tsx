import React, { useEffect, useRef, useState } from "react"
import { RuntimeOS } from "./RuntimeOS"

export interface RuntimeConsoleMessage {
  id: string
  timestamp: number
  level: "info" | "warn" | "error" | "runtime"
  message: string
}

export interface RuntimeConsoleProps {
  runtimeOS: RuntimeOS
}

export const RuntimeConsole: React.FC<RuntimeConsoleProps> = ({ runtimeOS }) => {
  const [messages, setMessages] = useState<RuntimeConsoleMessage[]>([])
  const [command, setCommand] = useState("")
  const scrollRef = useRef<HTMLDivElement>(null)

  const appendMessage = (
    input: Omit<RuntimeConsoleMessage, "id" | "timestamp">,
  ): void => {
    setMessages((previous) => [
      ...previous,
      {
        id: crypto.randomUUID(),
        timestamp: Date.now(),
        ...input,
      },
    ])
  }

  useEffect(() => {
    appendMessage({ level: "runtime", message: "Runtime console initialized" })
    appendMessage({ level: "info", message: "Runtime manifold synchronized" })
    appendMessage({ level: "info", message: "Replay subsystem online" })
  }, [])

  useEffect(() => {
    if (!scrollRef.current) return
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [messages])

  const executeCommand = (): void => {
    const trimmed = command.trim()
    if (!trimmed) return

    appendMessage({ level: "runtime", message: `> ${trimmed}` })

    switch (trimmed) {
      case "status":
        appendMessage({
          level: "info",
          message: JSON.stringify(runtimeOS.getMetrics(), null, 2),
        })
        break
      case "workspace":
        appendMessage({
          level: "info",
          message: JSON.stringify(runtimeOS.workspace.serialize(), null, 2),
        })
        break
      case "session":
        appendMessage({
          level: "info",
          message: JSON.stringify(runtimeOS.session.serialize(), null, 2),
        })
        break
      case "clear":
        setMessages([])
        break
      default:
        appendMessage({ level: "warn", message: `Unknown command: ${trimmed}` })
    }

    setCommand("")
  }

  const getMessageColor = (level: RuntimeConsoleMessage["level"]): string => {
    switch (level) {
      case "runtime":
        return "text-cyan-400"
      case "warn":
        return "text-yellow-400"
      case "error":
        return "text-red-400"
      default:
        return "text-neutral-300"
    }
  }

  return (
    <div className="flex h-full w-full flex-col bg-black font-mono text-neutral-100">
      <div className="flex h-10 shrink-0 items-center justify-between border-b border-neutral-800 bg-neutral-950 px-4">
        <div className="text-sm font-semibold">Runtime Console</div>
        <div className="text-[10px] opacity-50">deterministic execution surface</div>
      </div>

      <div ref={scrollRef} className="flex flex-1 flex-col gap-2 overflow-auto p-4">
        {messages.map((message) => (
          <div key={message.id} className="flex gap-3 break-all text-xs leading-relaxed">
            <div className="shrink-0 opacity-40">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
            <div className={getMessageColor(message.level)}>{message.message}</div>
          </div>
        ))}
      </div>

      <div className="flex shrink-0 items-center gap-3 border-t border-neutral-800 bg-neutral-950 p-3">
        <div className="text-sm text-cyan-400">❯</div>
        <input
          value={command}
          onChange={(event) => setCommand(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") executeCommand()
          }}
          placeholder="Enter runtime command..."
          className="flex-1 bg-transparent text-sm outline-none"
        />
        <button
          onClick={executeCommand}
          className="rounded-lg bg-cyan-600 px-3 py-1.5 text-xs font-semibold transition hover:bg-cyan-500"
        >
          Execute
        </button>
      </div>
    </div>
  )
}
