import React, { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react"

type Json = Record<string, any>

type ChatMessage = {
  role: "user" | "assistant"
  content: string
  metadata?: string
}

type AssistantMode = "GENERAL_CHAT" | "AGENTIC_APPLICATION_DEVELOPMENT" | "BOTH"

const ASSISTANT_MODE_STORAGE_KEY = "hhs.production.assistant.mode"
const SYSTEM_INSTRUCTION_STORAGE_KEY = "hhs.production.assistant.custom_system_instruction"
const MAX_SYSTEM_INSTRUCTION_CHARS = 8192

const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback
const short = (value: unknown): string => {
  const raw = text(value)
  return raw ? `${raw.slice(0, 10)}…${raw.slice(-6)}` : "—"
}

async function requestJson(url: string, init?: RequestInit, timeoutMs = 60000): Promise<Json> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal,
      headers: {
        accept: "application/json",
        ...(init?.body ? { "content-type": "application/json" } : {}),
        ...(init?.headers ?? {}),
      },
    })
    const raw = await response.text()
    let body: Json = {}
    try {
      body = raw ? record(JSON.parse(raw)) : {}
    } catch {
      body = { detail: raw || response.statusText }
    }
    if (!response.ok) {
      const detail = record(body.detail)
      throw new Error(text(detail.classification ?? detail.detail ?? body.detail ?? body.error ?? body.status, `${response.status} ${response.statusText}`))
    }
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

function receiptOf(turn: Json): string | null {
  for (const candidate of [
    record(turn.provider_invocation_receipt).provider_invocation_receipt_hash72,
    record(turn.provider_result_ingress).provider_result_ingress_root_hash72,
    turn.hhs_api_tool_trace_root_hash72,
    turn.turn_root_hash72,
  ]) {
    if (typeof candidate === "string" && candidate) return candidate
  }
  return null
}

function loadAssistantMode(): AssistantMode {
  try {
    const value = window.localStorage.getItem(ASSISTANT_MODE_STORAGE_KEY)
    if (value === "GENERAL_CHAT" || value === "AGENTIC_APPLICATION_DEVELOPMENT" || value === "BOTH") return value
  } catch {
    // Use the compatibility default.
  }
  return "BOTH"
}

function modeLabel(mode: AssistantMode): string {
  if (mode === "GENERAL_CHAT") return "General chat"
  if (mode === "AGENTIC_APPLICATION_DEVELOPMENT") return "Agentic application development"
  return "Both"
}

function loadSystemInstruction(): string {
  try {
    return window.localStorage.getItem(SYSTEM_INSTRUCTION_STORAGE_KEY) ?? ""
  } catch {
    return ""
  }
}

function legacyCopy(value: string): boolean {
  const node = document.createElement("textarea")
  node.value = value
  node.setAttribute("readonly", "true")
  node.style.position = "fixed"
  node.style.opacity = "0"
  node.style.pointerEvents = "none"
  document.body.appendChild(node)
  node.select()
  let ok = false
  try {
    ok = document.execCommand("copy")
  } finally {
    node.remove()
  }
  return ok
}

export interface ProductionAssistantChatProps {
  projectId: string | null
  vectorContextId?: string | null
  onOpenFiles: () => void
}

export const ProductionAssistantChat: React.FC<ProductionAssistantChatProps> = ({
  projectId,
  vectorContextId,
  onOpenFiles,
}) => {
  const [health, setHealth] = useState<Json>({})
  const [threadId, setThreadId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [assistantMode, setAssistantMode] = useState<AssistantMode>(loadAssistantMode)
  const [customSystemInstruction, setCustomSystemInstruction] = useState(loadSystemInstruction)
  const [clipboardNotice, setClipboardNotice] = useState<string | null>(null)
  const [copiedMessageIndex, setCopiedMessageIndex] = useState<number | null>(null)
  const scrollRef = useRef<HTMLDivElement | null>(null)

  const online = health.online !== false && Object.keys(health).length > 0
  const modelLabel = text(
    health.model_id
      ?? health.selected_model_id
      ?? health.selected_provider_id
      ?? health.effective_mode
      ?? health.status,
    online ? "assistant ready" : "assistant checking",
  )

  const latestReceipt = useMemo(() => {
    const assistant = [...messages].reverse().find((message) => message.role === "assistant" && message.metadata)
    return assistant?.metadata ?? "No assistant turn yet"
  }, [messages])

  const refreshHealth = async (): Promise<void> => {
    try {
      setHealth(await requestJson("/api/assistant/health", undefined, 10000))
      setError(null)
    } catch (reason) {
      setHealth({ online: false, status: "ASSISTANT_OFFLINE" })
      setError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  useEffect(() => {
    void refreshHealth()
    const interval = window.setInterval(() => void refreshHealth(), 15000)
    return () => window.clearInterval(interval)
  }, [])

  useEffect(() => {
    const node = scrollRef.current
    if (node) node.scrollTop = node.scrollHeight
  }, [messages, busy])

  const updateAssistantMode = (value: AssistantMode): void => {
    setAssistantMode(value)
    try {
      window.localStorage.setItem(ASSISTANT_MODE_STORAGE_KEY, value)
    } catch {
      // The selected mode still applies to this browser session.
    }
  }

  const updateSystemInstruction = (value: string): void => {
    const bounded = value.slice(0, MAX_SYSTEM_INSTRUCTION_CHARS)
    setCustomSystemInstruction(bounded)
    try {
      if (bounded) window.localStorage.setItem(SYSTEM_INSTRUCTION_STORAGE_KEY, bounded)
      else window.localStorage.removeItem(SYSTEM_INSTRUCTION_STORAGE_KEY)
    } catch {
      // The setting still applies to this browser session when storage is unavailable.
    }
  }

  const resetThread = (): void => {
    setThreadId(null)
    setMessages([])
    setInput("")
    setError(null)
  }

  const copyText = async (value: string, index: number): Promise<void> => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value)
      } else if (!legacyCopy(value)) {
        throw new Error("clipboard copy is unavailable")
      }
      setCopiedMessageIndex(index)
      setClipboardNotice("Copied")
      window.setTimeout(() => {
        setCopiedMessageIndex((current) => current === index ? null : current)
        setClipboardNotice(null)
      }, 1600)
    } catch (reason) {
      setClipboardNotice(reason instanceof Error ? reason.message : "Clipboard copy failed")
    }
  }

  const pasteClipboard = async (): Promise<void> => {
    setClipboardNotice(null)
    try {
      if (!navigator.clipboard?.readText) {
        throw new Error("Clipboard paste is unavailable here; use your device Paste command.")
      }
      const value = await navigator.clipboard.readText()
      if (!value) {
        setClipboardNotice("Clipboard is empty")
        return
      }
      setInput((current) => current ? `${current}${current.endsWith("\n") ? "" : "\n"}${value}` : value)
      setClipboardNotice("Pasted")
    } catch (reason) {
      setClipboardNotice(reason instanceof Error ? reason.message : "Clipboard paste failed")
    }
  }

  const send = async (event: FormEvent): Promise<void> => {
    event.preventDefault()
    const content = input.trim()
    if (!content || busy) return

    setBusy(true)
    setError(null)
    setInput("")
    setMessages((current) => [...current, { role: "user", content }])

    try {
      const instruction = customSystemInstruction.trim()
      const turn = await requestJson("/api/assistant/chat", {
        method: "POST",
        body: JSON.stringify({
          thread_id: threadId,
          project_id: projectId || "project:production-mobile-control",
          title: "HHS Mobile Assistant",
          metadata: {
            workspace_surface: "production_mobile_control",
            vector_identity_visible_to_user: vectorContextId || null,
            vector_payload_auto_attached_to_prompt: false,
            custom_system_instruction_present: Boolean(instruction),
            assistant_mode: assistantMode,
          },
          content,
          custom_system_instruction: instruction || null,
          assistant_mode: assistantMode,
        }),
      }, 120000)

      const nextThreadId = text(turn.thread_id ?? record(turn.thread).thread_id)
      if (nextThreadId) setThreadId(nextThreadId)

      const answer = text(
        record(turn.assistant_message).content
          ?? turn.response
          ?? turn.error,
        `Assistant turn completed with status ${text(turn.status, "UNKNOWN")}.`,
      )
      const receipt = receiptOf(turn)
      const providerMode = text(turn.effective_mode ?? turn.execution_backend ?? health.effective_mode)
      const returnedAssistantMode = text(turn.assistant_mode, assistantMode)
      const toolCount = Number.isInteger(turn.hhs_api_tool_call_count) ? Number(turn.hhs_api_tool_call_count) : 0
      const metadata = [
        modeLabel(
          returnedAssistantMode === "GENERAL_CHAT" || returnedAssistantMode === "AGENTIC_APPLICATION_DEVELOPMENT"
            ? returnedAssistantMode
            : "BOTH",
        ),
        providerMode,
        `${toolCount} HHS tool${toolCount === 1 ? "" : "s"}`,
        turn.custom_system_instruction_applied ? "custom instructions" : "",
        receipt ? `receipt ${short(receipt)}` : "",
      ].filter(Boolean).join(" · ")

      setMessages((current) => [...current, {
        role: "assistant",
        content: answer,
        metadata,
      }])
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : String(reason)
      setError(message)
      setMessages((current) => [...current, {
        role: "assistant",
        content: "The assistant request did not complete. No response or runtime mutation was fabricated.",
        metadata: message,
      }])
    } finally {
      setBusy(false)
    }
  }

  const onComposerKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>): void => {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault()
      event.currentTarget.form?.requestSubmit()
    }
  }

  return (
    <section data-testid="production-mobile-assistant" className="overflow-hidden rounded-3xl border border-cyan-950 bg-neutral-900/70 shadow-2xl">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-800 bg-black/35 px-4 py-3 md:px-5">
        <div className="min-w-0">
          <div className="text-[10px] uppercase tracking-[0.22em] text-cyan-500">Natural-language control</div>
          <h2 className="mt-1 text-base font-semibold text-white md:text-lg">HHS Assistant</h2>
          <div className="mt-1 text-[10px] text-neutral-500">{modeLabel(assistantMode)}</div>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={() => void refreshHealth()} className="rounded-full border border-neutral-800 bg-black/50 px-3 py-1.5 text-[10px] text-neutral-400">
            <span className={`mr-1.5 inline-block h-2 w-2 rounded-full ${online ? "bg-emerald-400" : "bg-amber-400"}`} />
            {modelLabel}
          </button>
          <button type="button" onClick={() => setSettingsOpen((value) => !value)} className="runtime-button min-h-9 px-3 text-xs" aria-expanded={settingsOpen}>Settings</button>
          <button type="button" onClick={resetThread} className="runtime-button min-h-9 px-3 text-xs">New chat</button>
        </div>
      </header>

      {settingsOpen ? (
        <section data-testid="assistant-settings" className="border-b border-neutral-800 bg-neutral-950/95 p-3 md:p-4">
          <div className="mx-auto max-w-4xl">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-white">Assistant settings</h3>
                <p className="mt-1 text-[11px] leading-5 text-neutral-500">Customize how the language model responds. These instructions are added to the inherited HHS system instruction; they do not replace runtime authority controls.</p>
              </div>
              <button type="button" onClick={() => setSettingsOpen(false)} className="runtime-button min-h-9 px-3 text-xs">Done</button>
            </div>
            <label className="mt-3 block">
              <span className="text-[10px] uppercase tracking-[0.14em] text-neutral-500">Assistant mode</span>
              <select
                data-testid="assistant-mode"
                value={assistantMode}
                onChange={(event) => updateAssistantMode(event.target.value as AssistantMode)}
                className="runtime-input mt-2 min-h-11 w-full"
              >
                <option value="GENERAL_CHAT">General chat</option>
                <option value="AGENTIC_APPLICATION_DEVELOPMENT">Agentic application development</option>
                <option value="BOTH">Both</option>
              </select>
              <span className="mt-1 block text-[10px] leading-4 text-neutral-600">
                General chat keeps developer tools off. Agentic application development focuses on code and governed workspace work. Both switches naturally between conversation and development.
              </span>
            </label>
            <label className="mt-3 block">
              <span className="text-[10px] uppercase tracking-[0.14em] text-neutral-500">System instructions</span>
              <textarea
                data-testid="assistant-system-instructions"
                value={customSystemInstruction}
                onChange={(event) => updateSystemInstruction(event.target.value)}
                maxLength={MAX_SYSTEM_INSTRUCTION_CHARS}
                rows={6}
                placeholder="Example: Be concise, explain technical ideas in plain English, and use short paragraphs."
                className="mt-2 min-h-32 w-full resize-y rounded-2xl border border-neutral-700 bg-black/60 p-3 text-sm leading-6 text-neutral-200 outline-none focus:border-cyan-700"
              />
            </label>
            <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-[10px] text-neutral-600">
              <span>{customSystemInstruction.length} / {MAX_SYSTEM_INSTRUCTION_CHARS}</span>
              <button type="button" onClick={() => updateSystemInstruction("")} className="runtime-button min-h-9 px-3 text-xs">Clear instructions</button>
            </div>
          </div>
        </section>
      ) : null}

      {error ? <div className="border-b border-red-900/60 bg-red-950/20 px-4 py-2 text-xs text-red-200">{error}</div> : null}

      <div ref={scrollRef} className="flex min-h-[42vh] max-h-[62vh] flex-col gap-3 overflow-y-auto bg-[radial-gradient(circle_at_top,rgba(8,145,178,.08),transparent_46%)] p-3 md:min-h-[460px] md:p-5">
        {messages.length === 0 ? (
          <div className="m-auto max-w-xl text-center">
            <div className="text-lg font-semibold text-white">How can I help?</div>
            <p className="mt-2 text-xs leading-5 text-neutral-500">
              {assistantMode === "GENERAL_CHAT"
                ? "Chat naturally about any topic supported by the configured language model."
                : assistantMode === "AGENTIC_APPLICATION_DEVELOPMENT"
                  ? "Describe the application, code, runtime, test, or deployment work you want to develop."
                  : "Chat naturally, or ask for governed application-development work when you need it."}
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {[
                "Summarize the current runtime state.",
                "Explain the latest Hash216 receipt in plain language.",
                "What can I do with the files in this workspace?",
              ].map((prompt) => (
                <button key={prompt} type="button" onClick={() => setInput(prompt)} className="rounded-full border border-neutral-800 bg-black/50 px-3 py-2 text-[11px] text-neutral-300 hover:border-cyan-800">
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : messages.map((message, index) => (
          <article
            key={`${message.role}:${index}`}
            className={`group max-w-[92%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 ${message.role === "user" ? "ml-auto border border-cyan-800/50 bg-cyan-950/40 text-white" : "mr-auto border border-neutral-800 bg-black/45 text-neutral-200"}`}
          >
            <div>{message.content}</div>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <button type="button" onClick={() => void copyText(message.content, index)} className="min-h-8 rounded-lg border border-neutral-800 bg-black/30 px-2.5 text-[10px] text-neutral-400 hover:border-cyan-800 hover:text-cyan-200">
                {copiedMessageIndex === index ? "Copied" : "Copy"}
              </button>
              {message.metadata ? <div className="font-mono text-[9px] leading-4 text-neutral-500">{message.metadata}</div> : null}
            </div>
          </article>
        ))}

        {busy ? (
          <div className="mr-auto rounded-2xl border border-neutral-800 bg-black/45 px-4 py-3 text-xs text-neutral-400">
            Generating response…
          </div>
        ) : null}
      </div>

      <form onSubmit={(event) => void send(event)} className="border-t border-neutral-800 bg-black/55 p-3 md:p-4">
        <div className="rounded-2xl border border-neutral-700 bg-neutral-950 p-2 focus-within:border-cyan-700">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={onComposerKeyDown}
            placeholder="Message HHS…"
            rows={2}
            className="max-h-40 min-h-16 w-full resize-none bg-transparent px-2 py-2 text-sm leading-6 text-white outline-none placeholder:text-neutral-600"
            aria-label="Message HHS assistant"
          />
          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-neutral-900 pt-2">
            <div className="flex items-center gap-2">
              <button type="button" onClick={onOpenFiles} className="runtime-button min-h-10 px-3 text-xs">Files</button>
              <button type="button" onClick={() => void pasteClipboard()} className="runtime-button min-h-10 px-3 text-xs">Paste</button>
              <span className="hidden text-[9px] text-neutral-600 sm:inline">
                {vectorContextId ? `hydrated vector ${short(vectorContextId)} visible` : "no hydrated vector selected"}
              </span>
            </div>
            <button type="submit" disabled={busy || !input.trim()} className="min-h-10 rounded-xl bg-cyan-700 px-5 text-sm font-semibold text-white transition hover:bg-cyan-600 disabled:cursor-not-allowed disabled:bg-neutral-800 disabled:text-neutral-500">
              {busy ? "Working…" : "Send"}
            </button>
          </div>
        </div>
        <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-[9px] leading-4 text-neutral-600">
          <span>{clipboardNotice ? `${clipboardNotice} · ` : ""}Enter sends · Shift+Enter adds a line</span>
          <span>File/vector ingress is user-controlled; uploaded payloads are not automatically attached to assistant prompts.</span>
        </div>
      </form>

      <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-neutral-900 bg-black/35 px-4 py-2 font-mono text-[9px] text-neutral-600">
        <span>thread={threadId ? short(threadId) : "new"} · {modeLabel(assistantMode)}</span>
        <span>{latestReceipt}</span>
      </footer>
    </section>
  )
}

export default ProductionAssistantChat
