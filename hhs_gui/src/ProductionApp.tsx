import React, { FormEvent, useEffect, useMemo, useState } from "react"

type JsonRecord = Record<string, any>
type ViewId = "assistant" | "runtime" | "capabilities" | "harmonicode" | "receipts"
type ChatMessage = {
    role: "user" | "assistant"
    content: string
    metadata?: string
}
type ReceiptRecord = {
    id: string
    kind: string
    createdAt: string
    payload: JsonRecord
}

const NAVIGATION: Array<{ id: ViewId; label: string }> = [
    { id: "assistant", label: "Assistant" },
    { id: "runtime", label: "Runtime" },
    { id: "capabilities", label: "Capabilities" },
    { id: "harmonicode", label: "HARMONICODE" },
    { id: "receipts", label: "Receipts" },
]

const RUNTIME_SURFACES = [
    ["state", "Runtime state"],
    ["services", "Registered services"],
    ["service-status", "Service status"],
    ["invariants", "Kernel invariants"],
    ["conformance", "Kernel conformance"],
    ["pass152", "Pass 152 status"],
    ["pass152-capabilities", "Pass 152 capabilities"],
] as const

async function requestJson<T = JsonRecord>(url: string, init?: RequestInit): Promise<T> {
    const response = await fetch(url, {
        ...init,
        headers: {
            Accept: "application/json",
            ...(init?.body ? { "Content-Type": "application/json" } : {}),
            ...(init?.headers ?? {}),
        },
    })
    const text = await response.text()
    let payload: any = {}
    try {
        payload = text ? JSON.parse(text) : {}
    } catch {
        payload = { ok: false, error: text || `Non-JSON response from ${url}` }
    }
    if (!response.ok) {
        const detail = payload?.detail ?? payload?.error ?? payload?.status ?? response.statusText
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail))
    }
    return payload as T
}

function shortHash(value: unknown): string {
    const text = typeof value === "string" ? value : ""
    return text ? `${text.slice(0, 18)}…` : "none"
}

function turnReceipt(turn: JsonRecord): string | undefined {
    return turn?.provider_invocation_receipt?.provider_invocation_receipt_hash72
        ?? turn?.provider_result_ingress?.provider_result_ingress_root_hash72
        ?? turn?.hhs_api_tool_trace_root_hash72
        ?? turn?.turn_root_hash72
}

function errorText(error: unknown): string {
    return error instanceof Error ? error.message : String(error)
}

function JsonPanel({ value, empty = "No result yet." }: { value: unknown; empty?: string }) {
    return (
        <pre className="hhs-json">
            {value == null ? empty : JSON.stringify(value, null, 2)}
        </pre>
    )
}

export default function ProductionApp() {
    const [view, setView] = useState<ViewId>("assistant")
    const [systemStatus, setSystemStatus] = useState<JsonRecord | null>(null)
    const [assistantHealth, setAssistantHealth] = useState<JsonRecord | null>(null)
    const [toolRegistry, setToolRegistry] = useState<JsonRecord | null>(null)
    const [productCapabilities, setProductCapabilities] = useState<JsonRecord | null>(null)
    const [startupError, setStartupError] = useState<string | null>(null)

    const [threadId, setThreadId] = useState<string | null>(null)
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [assistantInput, setAssistantInput] = useState("")
    const [assistantBusy, setAssistantBusy] = useState(false)
    const [lastTurn, setLastTurn] = useState<JsonRecord | null>(null)

    const [runtimeResult, setRuntimeResult] = useState<JsonRecord | null>(null)
    const [runtimeBusy, setRuntimeBusy] = useState<string | null>(null)
    const [toolResult, setToolResult] = useState<JsonRecord | null>(null)
    const [toolBusy, setToolBusy] = useState<string | null>(null)

    const [source, setSource] = useState(() => {
        try {
            return localStorage.getItem("hhs.production.harmonicode.source") ?? ""
        } catch {
            return ""
        }
    })
    const [analysisResult, setAnalysisResult] = useState<JsonRecord | null>(null)
    const [analysisBusy, setAnalysisBusy] = useState(false)
    const [receipts, setReceipts] = useState<ReceiptRecord[]>([])

    useEffect(() => {
        document.documentElement.dataset.hhsMounted = "true"
        document.getElementById("runtime_boot_overlay")?.remove()

        let active = true
        Promise.allSettled([
            requestJson<JsonRecord>("/api/system/status"),
            requestJson<JsonRecord>("/api/assistant/health"),
            requestJson<JsonRecord>("/api/assistant/tools"),
            requestJson<JsonRecord>("/api/product/capabilities"),
        ]).then((results) => {
            if (!active) return
            const [system, health, tools, capabilities] = results
            if (system.status === "fulfilled") setSystemStatus(system.value)
            if (health.status === "fulfilled") setAssistantHealth(health.value)
            if (tools.status === "fulfilled") setToolRegistry(tools.value)
            if (capabilities.status === "fulfilled") setProductCapabilities(capabilities.value)
            const failures = results
                .filter((item): item is PromiseRejectedResult => item.status === "rejected")
                .map((item) => errorText(item.reason))
            if (failures.length) setStartupError(failures.join(" | "))
        })

        return () => {
            active = false
        }
    }, [])

    const effectiveAssistantMode = assistantHealth?.effective_mode
        ?? assistantHealth?.status
        ?? "checking"
    const modelOnline = Boolean(assistantHealth?.model_online)
    const assistantOnline = assistantHealth?.online !== false
    const capabilityList: JsonRecord[] = Array.isArray(productCapabilities?.capabilities)
        ? productCapabilities.capabilities
        : []
    const tools: JsonRecord[] = Array.isArray(toolRegistry?.tools)
        ? toolRegistry.tools
        : []

    const receiptSummary = useMemo(() => {
        const latest = receipts.at(-1)
        return latest ? `${latest.kind} · ${shortHash(latest.id)}` : "No receipts recorded"
    }, [receipts])

    function recordReceipt(kind: string, payload: JsonRecord, id?: string) {
        setReceipts((current) => [
            ...current,
            {
                id: id ?? `local:${Date.now()}`,
                kind,
                createdAt: new Date().toISOString(),
                payload,
            },
        ].slice(-100))
    }

    async function sendAssistantMessage(event: FormEvent) {
        event.preventDefault()
        const content = assistantInput.trim()
        if (!content || assistantBusy) return

        setAssistantBusy(true)
        setAssistantInput("")
        setMessages((current) => [...current, { role: "user", content }])

        try {
            const turn = await requestJson<JsonRecord>("/api/assistant/chat", {
                method: "POST",
                body: JSON.stringify({
                    thread_id: threadId,
                    project_id: "project:public-runtime-os",
                    title: "HHS Production Assistant",
                    content,
                }),
            })
            const resolvedThreadId = turn.thread_id ?? turn.thread?.thread_id
            if (typeof resolvedThreadId === "string") setThreadId(resolvedThreadId)
            setLastTurn(turn)

            const answer = String(
                turn?.assistant_message?.content
                ?? turn?.error
                ?? `Assistant turn completed with status ${turn?.status ?? "UNKNOWN"}.`,
            )
            const metadata = [
                turn?.effective_mode ?? turn?.execution_backend,
                `${turn?.hhs_api_tool_call_count ?? 0} HHS tool call(s)`,
                `receipt ${shortHash(turnReceipt(turn))}`,
            ].filter(Boolean).join(" · ")
            setMessages((current) => [...current, {
                role: "assistant",
                content: answer,
                metadata,
            }])

            recordReceipt("assistant_turn", turn, turnReceipt(turn))
        } catch (error) {
            setMessages((current) => [...current, {
                role: "assistant",
                content: `Assistant request failed: ${errorText(error)}`,
                metadata: "No assistant result or runtime mutation was fabricated.",
            }])
        } finally {
            setAssistantBusy(false)
        }
    }

    async function loadRuntimeSurface(surface: string) {
        setRuntimeBusy(surface)
        try {
            const result = await requestJson<JsonRecord>(`/api/runtime/read/${encodeURIComponent(surface)}`)
            setRuntimeResult(result)
            recordReceipt("runtime_read", result, result?.tool_receipt_root_hash72)
        } catch (error) {
            setRuntimeResult({ ok: false, error: errorText(error), surface })
        } finally {
            setRuntimeBusy(null)
        }
    }

    async function executeTool(name: string) {
        setToolBusy(name)
        try {
            const result = await requestJson<JsonRecord>(`/api/assistant/tools/${encodeURIComponent(name)}`, {
                method: "POST",
                body: JSON.stringify({ arguments: {} }),
            })
            setToolResult(result)
            recordReceipt("assistant_tool", result, result?.tool_receipt_root_hash72)
        } catch (error) {
            setToolResult({ ok: false, error: errorText(error), tool_name: name })
        } finally {
            setToolBusy(null)
        }
    }

    async function analyzeHarmonicode(event: FormEvent) {
        event.preventDefault()
        const normalized = source.trim()
        if (!normalized || analysisBusy) return
        setAnalysisBusy(true)
        try {
            localStorage.setItem("hhs.production.harmonicode.source", source)
            const result = await requestJson<JsonRecord>("/api/workspace/harmonicode/analyze", {
                method: "POST",
                body: JSON.stringify({ source }),
            })
            setAnalysisResult(result)
            const id = result?.result?.document?.document_root_hash72
                ?? result?.result?.typed_ir?.ir_root_hash72
                ?? result?.analysis_id
            recordReceipt("harmonicode_analysis", result, id)
        } catch (error) {
            setAnalysisResult({ ok: false, error: errorText(error) })
        } finally {
            setAnalysisBusy(false)
        }
    }

    return (
        <div className="hhs-production-shell">
            <header className="hhs-topbar">
                <div className="hhs-brand">
                    <div className="hhs-mark">H</div>
                    <div>
                        <strong>HHS Runtime OS</strong>
                        <small>Production visual IDE · callable surfaces only</small>
                    </div>
                </div>
                <div className="hhs-status-row">
                    <span className={`hhs-chip ${assistantOnline ? "online" : "warn"}`}>
                        assistant {assistantOnline ? "online" : "offline"}
                    </span>
                    <span className={`hhs-chip ${modelOnline ? "online" : "warn"}`}>
                        model {modelOnline ? "online" : "deterministic HHS mode"}
                    </span>
                    <span className="hhs-chip warn">runtime authority read-only</span>
                </div>
            </header>

            <div className="hhs-layout">
                <nav className="hhs-sidebar" aria-label="Runtime OS sections">
                    {NAVIGATION.map((item) => (
                        <button
                            key={item.id}
                            className={`hhs-nav-button ${view === item.id ? "active" : ""}`}
                            onClick={() => setView(item.id)}
                            type="button"
                        >
                            {item.label}
                        </button>
                    ))}
                    <div className="hhs-sidebar-note">
                        Only implemented API surfaces appear here. Canonical mutation controls remain hidden while runtime authority is detached.
                    </div>
                </nav>

                <main className="hhs-main">
                    {startupError && (
                        <div className="hhs-panel hhs-error" style={{ marginBottom: 14 }}>
                            <div className="hhs-panel-body">Some status projections failed: {startupError}</div>
                        </div>
                    )}

                    {view === "assistant" && (
                        <section className="hhs-view">
                            <div className="hhs-view-header">
                                <div>
                                    <h1>Natural-language assistant</h1>
                                    <p>Queries use the configured governed model when available and fall back to deterministic HHS tool-backed answers. Responses never simulate runtime mutation.</p>
                                </div>
                                <button className="hhs-secondary" type="button" onClick={() => {
                                    setThreadId(null)
                                    setMessages([])
                                    setLastTurn(null)
                                }}>New thread</button>
                            </div>

                            <div className="hhs-assistant-grid">
                                <div className="hhs-panel hhs-chat-panel">
                                    <div className="hhs-panel-head">
                                        <strong>HHS conversation</strong>
                                        <span className="hhs-chip">{threadId ? shortHash(threadId) : "new thread"}</span>
                                    </div>
                                    <div className="hhs-messages" aria-live="polite">
                                        {messages.length === 0 ? (
                                            <div className="hhs-empty">
                                                Enter a question about runtime state, services, invariants, Pass status, capabilities, or HARMONICODE. No suggestion prompt is auto-submitted.
                                            </div>
                                        ) : messages.map((message, index) => (
                                            <article className={`hhs-message ${message.role}`} key={`${message.role}-${index}`}>
                                                {message.content}
                                                {message.metadata && <small>{message.metadata}</small>}
                                            </article>
                                        ))}
                                    </div>
                                    <form className="hhs-composer" onSubmit={sendAssistantMessage}>
                                        <textarea
                                            value={assistantInput}
                                            onChange={(event) => setAssistantInput(event.target.value)}
                                            placeholder="Ask HHS…"
                                            rows={3}
                                            required
                                        />
                                        <button className="hhs-primary" disabled={assistantBusy} type="submit">
                                            {assistantBusy ? "Processing…" : "Send"}
                                        </button>
                                    </form>
                                </div>

                                <aside className="hhs-panel">
                                    <div className="hhs-panel-head"><strong>Assistant state</strong></div>
                                    <div className="hhs-panel-body hhs-metadata">
                                        <div className="hhs-field"><span>Effective mode</span><strong>{effectiveAssistantMode}</strong></div>
                                        <div className="hhs-field"><span>Model provider</span><strong>{modelOnline ? "available" : "not connected"}</strong></div>
                                        <div className="hhs-field"><span>HHS tools</span><strong>{toolRegistry?.tool_names?.length ?? tools.length} registered</strong></div>
                                        <div className="hhs-field"><span>Latest receipt</span><strong>{receiptSummary}</strong></div>
                                        <div className="hhs-field"><span>Runtime mutation</span><strong>not admitted</strong></div>
                                        {lastTurn && <JsonPanel value={lastTurn?.hhs_api_tool_trace ?? []} empty="No tools used." />}
                                    </div>
                                </aside>
                            </div>
                        </section>
                    )}

                    {view === "runtime" && (
                        <section className="hhs-view">
                            <div className="hhs-view-header">
                                <div>
                                    <h1>Runtime evidence</h1>
                                    <p>These controls execute actual governed read-only HHS functions and return their receipt envelopes.</p>
                                </div>
                            </div>
                            <div className="hhs-panel">
                                <div className="hhs-panel-head"><strong>Read surfaces</strong></div>
                                <div className="hhs-panel-body">
                                    <div className="hhs-toolbar">
                                        {RUNTIME_SURFACES.map(([surface, label]) => (
                                            <button className="hhs-secondary" type="button" key={surface} onClick={() => loadRuntimeSurface(surface)} disabled={runtimeBusy !== null}>
                                                {runtimeBusy === surface ? "Loading…" : label}
                                            </button>
                                        ))}
                                    </div>
                                    <div style={{ marginTop: 14 }}><JsonPanel value={runtimeResult} /></div>
                                </div>
                            </div>
                        </section>
                    )}

                    {view === "capabilities" && (
                        <section className="hhs-view">
                            <div className="hhs-view-header">
                                <div>
                                    <h1>Callable capabilities</h1>
                                    <p>Capabilities are derived from the public product API. Features that are not callable are not presented as application controls.</p>
                                </div>
                            </div>
                            <div className="hhs-card-grid">
                                {capabilityList.map((capability) => (
                                    <article className="hhs-card" key={String(capability.id)}>
                                        <h3>{String(capability.title ?? capability.id)}</h3>
                                        <p>{capability.callable ? "Callable now" : "Unavailable"}</p>
                                        <code>{String(capability.endpoint ?? "")}</code>
                                    </article>
                                ))}
                            </div>
                            <div className="hhs-split">
                                <div className="hhs-panel">
                                    <div className="hhs-panel-head"><strong>Governed assistant tools</strong></div>
                                    <div className="hhs-panel-body hhs-tool-list">
                                        {tools.map((tool) => {
                                            const definition = tool.function ?? {}
                                            const name = String(definition.name ?? "")
                                            return (
                                                <div className="hhs-tool-row" key={name}>
                                                    <div>
                                                        <strong>{name}</strong>
                                                        <small>{String(definition.description ?? "")}</small>
                                                    </div>
                                                    <button className="hhs-secondary" type="button" disabled={toolBusy !== null} onClick={() => executeTool(name)}>
                                                        {toolBusy === name ? "Running…" : "Run"}
                                                    </button>
                                                </div>
                                            )
                                        })}
                                    </div>
                                </div>
                                <div className="hhs-panel">
                                    <div className="hhs-panel-head"><strong>Tool result</strong></div>
                                    <div className="hhs-panel-body"><JsonPanel value={toolResult} /></div>
                                </div>
                            </div>
                        </section>
                    )}

                    {view === "harmonicode" && (
                        <section className="hhs-view">
                            <div className="hhs-view-header">
                                <div>
                                    <h1>HARMONICODE workspace</h1>
                                    <p>The editor invokes the repository-native language service and returns normalized source, AST, typed IR, symbol data, and validation. It does not claim program execution.</p>
                                </div>
                            </div>
                            <div className="hhs-split">
                                <form className="hhs-panel" onSubmit={analyzeHarmonicode}>
                                    <div className="hhs-panel-head"><strong>Source editor</strong></div>
                                    <div className="hhs-panel-body">
                                        <textarea
                                            className="hhs-editor-textarea"
                                            value={source}
                                            onChange={(event) => setSource(event.target.value)}
                                            placeholder="Enter HARMONICODE source"
                                            rows={18}
                                            required
                                        />
                                        <div className="hhs-toolbar" style={{ marginTop: 10 }}>
                                            <button className="hhs-primary" disabled={analysisBusy} type="submit">
                                                {analysisBusy ? "Analyzing…" : "Parse and build typed IR"}
                                            </button>
                                            <button className="hhs-secondary" type="button" onClick={() => {
                                                setSource("")
                                                setAnalysisResult(null)
                                                localStorage.removeItem("hhs.production.harmonicode.source")
                                            }}>Clear</button>
                                        </div>
                                    </div>
                                </form>
                                <div className="hhs-panel">
                                    <div className="hhs-panel-head"><strong>Language-service result</strong></div>
                                    <div className="hhs-panel-body"><JsonPanel value={analysisResult} /></div>
                                </div>
                            </div>
                        </section>
                    )}

                    {view === "receipts" && (
                        <section className="hhs-view">
                            <div className="hhs-view-header">
                                <div>
                                    <h1>Receipt ledger</h1>
                                    <p>This session view records actual assistant turns, tool calls, runtime reads, and language analyses returned by the server.</p>
                                </div>
                                <button className="hhs-secondary" type="button" onClick={() => setReceipts([])}>Clear session view</button>
                            </div>
                            {receipts.length === 0 ? (
                                <div className="hhs-panel"><div className="hhs-empty">No server receipts have been returned in this browser session.</div></div>
                            ) : (
                                <div className="hhs-card-grid">
                                    {[...receipts].reverse().map((receipt, index) => (
                                        <article className="hhs-card" key={`${receipt.id}-${index}`}>
                                            <h3>{receipt.kind}</h3>
                                            <p>{receipt.createdAt}</p>
                                            <code>{receipt.id}</code>
                                            <details style={{ marginTop: 10 }}>
                                                <summary>Inspect payload</summary>
                                                <JsonPanel value={receipt.payload} />
                                            </details>
                                        </article>
                                    ))}
                                </div>
                            )}
                        </section>
                    )}
                </main>
            </div>
        </div>
    )
}
