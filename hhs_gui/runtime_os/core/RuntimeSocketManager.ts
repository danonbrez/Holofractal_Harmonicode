/**
 * =========================================================
 * RuntimeSocketManager
 * =========================================================
 *
 * Canonical Runtime OS websocket transport authority.
 *
 * Responsibilities:
 *
 * - Runtime stream ingestion
 * - Replay stream ingestion
 * - Graph stream ingestion
 * - Transport stream ingestion
 * - Connection lifecycle
 * - Event parsing
 * - Event history
 * - Runtime dispatch
 * - Frontend synchronization
 *
 * IMPORTANT:
 * ---------------------------------------------------------
 * Frontend transport is a projection layer.
 * Runtime authority belongs to the backend runtime.
 */

export type RuntimeEventType =

    | "runtime"
    | "replay"
    | "graph"
    | "transport"
    | "receipt"
    | "certification"

export interface RuntimeSocketConfig {

    runtimeEndpoint: string

    replayEndpoint: string

    graphEndpoint: string

    transportEndpoint: string

    reconnectDelayMs?: number
}

export interface RuntimeSocketState {

    runtimeConnected: boolean

    replayConnected: boolean

    graphConnected: boolean

    transportConnected: boolean

    lastRuntimeEvent?: RuntimeSocketEvent

    lastReplayEvent?: RuntimeSocketEvent

    lastGraphEvent?: RuntimeSocketEvent

    lastTransportEvent?: RuntimeSocketEvent

    runtimeHistory: RuntimeSocketEvent[]

    replayHistory: RuntimeSocketEvent[]

    graphHistory: RuntimeSocketEvent[]

    transportHistory: RuntimeSocketEvent[]

    totalEvents: number
}

export interface RuntimeSocketEvent {

    event_type: RuntimeEventType

    timestamp_ns: number

    sequence_id?: number

    authority?: string

    runtime_id?: string

    branch_id?: string

    event_hash72?: string

    parent_event_hash72?: string

    receipt_hash72?: string

    payload: Record<
        string,
        unknown
    >
}

export type RuntimeSocketListener = (

    event: RuntimeSocketEvent

) => void

// =========================================================
// RuntimeSocketManager
// =========================================================

export class RuntimeSocketManager {

    public readonly config:
        RuntimeSocketConfig

    public readonly state:
        RuntimeSocketState

    private runtimeSocket?:
        WebSocket

    private replaySocket?:
        WebSocket

    private graphSocket?:
        WebSocket

    private transportSocket?:
        WebSocket

    private listeners:
        Map<
            RuntimeEventType,
            Set<RuntimeSocketListener>
        >

    private readonly maxHistory =
        2048

    private readonly reconnectDelayMs:
        number

    private shutdownRequested =
        false

    // =====================================================
    // Constructor
    // =====================================================

    constructor(
        config: RuntimeSocketConfig
    ) {

        this.config = config

        this.listeners =
            new Map()

        this.reconnectDelayMs =
            config.reconnectDelayMs
            ??
            3000

        this.state = {

            runtimeConnected: false,

            replayConnected: false,

            graphConnected: false,

            transportConnected: false,

            runtimeHistory: [],

            replayHistory: [],

            graphHistory: [],

            transportHistory: [],

            totalEvents: 0
        }
    }

    // =====================================================
    // Initialize
    // =====================================================

    public async initialize():
        Promise<void> {

        this.shutdownRequested = false

        this.connectRuntime()

        this.connectReplay()

        this.connectGraph()

        this.connectTransport()
    }

    // =====================================================
    // Runtime
    // =====================================================

    private connectRuntime():
        void {

        this.runtimeSocket =
            new WebSocket(

                this.toSocketURL(
                    this.config
                        .runtimeEndpoint
                )
            )

        this.runtimeSocket.onopen =
            () => {

            this.state
                .runtimeConnected = true

            console.log(
                "[runtime/ws] connected"
            )
        }

        this.runtimeSocket.onclose =
            () => {

            this.state
                .runtimeConnected = false

            console.log(
                "[runtime/ws] disconnected"
            )

            this.scheduleReconnect(
                "runtime"
            )
        }

        this.runtimeSocket.onerror =
            (error) => {

            console.error(
                "[runtime/ws] error",
                error
            )
        }

        this.runtimeSocket.onmessage =
            (message) => {

            this.handleEvent(

                "runtime",

                message.data
            )
        }
    }

    // =====================================================
    // Replay
    // =====================================================

    private connectReplay():
        void {

        this.replaySocket =
            new WebSocket(

                this.toSocketURL(
                    this.config
                        .replayEndpoint
                )
            )

        this.replaySocket.onopen =
            () => {

            this.state
                .replayConnected = true

            console.log(
                "[replay/ws] connected"
            )
        }

        this.replaySocket.onclose =
            () => {

            this.state
                .replayConnected = false

            console.log(
                "[replay/ws] disconnected"
            )

            this.scheduleReconnect(
                "replay"
            )
        }

        this.replaySocket.onerror =
            (error) => {

            console.error(
                "[replay/ws] error",
                error
            )
        }

        this.replaySocket.onmessage =
            (message) => {

            this.handleEvent(

                "replay",

                message.data
            )
        }
    }

    // =====================================================
    // Graph
    // =====================================================

    private connectGraph():
        void {

        this.graphSocket =
            new WebSocket(

                this.toSocketURL(
                    this.config
                        .graphEndpoint
                )
            )

        this.graphSocket.onopen =
            () => {

            this.state
                .graphConnected = true

            console.log(
                "[graph/ws] connected"
            )
        }

        this.graphSocket.onclose =
            () => {

            this.state
                .graphConnected = false

            console.log(
                "[graph/ws] disconnected"
            )

            this.scheduleReconnect(
                "graph"
            )
        }

        this.graphSocket.onerror =
            (error) => {

            console.error(
                "[graph/ws] error",
                error
            )
        }

        this.graphSocket.onmessage =
            (message) => {

            this.handleEvent(

                "graph",

                message.data
            )
        }
    }

    // =====================================================
    // Transport
    // =====================================================

    private connectTransport():
        void {

        this.transportSocket =
            new WebSocket(

                this.toSocketURL(
                    this.config
                        .transportEndpoint
                )
            )

        this.transportSocket.onopen =
            () => {

            this.state
                .transportConnected = true

            console.log(
                "[transport/ws] connected"
            )
        }

        this.transportSocket.onclose =
            () => {

            this.state
                .transportConnected = false

            console.log(
                "[transport/ws] disconnected"
            )

            this.scheduleReconnect(
                "transport"
            )
        }

        this.transportSocket.onerror =
            (error) => {

            console.error(
                "[transport/ws] error",
                error
            )
        }

        this.transportSocket.onmessage =
            (message) => {

            this.handleEvent(

                "transport",

                message.data
            )
        }
    }

    // =====================================================
    // Event Handling
    // =====================================================

    private handleEvent(

        channel:
            RuntimeEventType,

        raw:
            string

    ): void {

        try {

            const parsed =
                this.normalizeEvent(
                    channel,
                    JSON.parse(raw)
                )

            this.dispatchEvent(
                parsed
            )

            this.appendHistory(
                channel,
                parsed
            )

            this.state.totalEvents += 1

            switch (channel) {

                case "runtime":

                    this.state
                        .lastRuntimeEvent =
                            parsed

                    break

                case "replay":

                    this.state
                        .lastReplayEvent =
                            parsed

                    break

                case "graph":

                    this.state
                        .lastGraphEvent =
                            parsed

                    break

                case "transport":

                    this.state
                        .lastTransportEvent =
                            parsed

                    break
            }

        } catch (error) {

            console.error(

                "[RuntimeSocketManager] parse failure",

                error
            )
        }
    }

    // =====================================================
    // Event Normalization
    // =====================================================

    private normalizeEvent(

        channel:
            RuntimeEventType,

        raw:
            Record<string, unknown>

    ): RuntimeSocketEvent {

        const payload =

            typeof raw.payload === "object"
            && raw.payload !== null
                ? raw.payload as Record<string, unknown>
                : {}

        return {

            event_type:
                (
                    raw.event_type
                    ??
                    raw.event
                    ??
                    channel
                ) as RuntimeEventType,

            timestamp_ns:
                Number(
                    raw.timestamp_ns
                    ??
                    Date.now() * 1_000_000
                ),

            sequence_id:
                typeof raw.sequence_id === "number"
                    ? raw.sequence_id
                    : undefined,

            authority:
                typeof raw.authority === "string"
                    ? raw.authority
                    : undefined,

            runtime_id:
                typeof raw.runtime_id === "string"
                    ? raw.runtime_id
                    : undefined,

            branch_id:
                typeof raw.branch_id === "string"
                    ? raw.branch_id
                    : undefined,

            event_hash72:
                typeof raw.event_hash72 === "string"
                    ? raw.event_hash72
                    : undefined,

            parent_event_hash72:
                typeof raw.parent_event_hash72 === "string"
                    ? raw.parent_event_hash72
                    : undefined,

            receipt_hash72:
                typeof raw.receipt_hash72 === "string"
                    ? raw.receipt_hash72
                    : undefined,

            payload
        }
    }

    // =====================================================
    // Reconnect
    // =====================================================

    private scheduleReconnect(
        channel: RuntimeEventType
    ): void {

        if (
            this.shutdownRequested
        ) {

            return
        }

        window.setTimeout(
            () => {

                if (
                    this.shutdownRequested
                ) {

                    return
                }

                switch (channel) {

                    case "runtime":

                        this.connectRuntime()

                        break

                    case "replay":

                        this.connectReplay()

                        break

                    case "graph":

                        this.connectGraph()

                        break

                    case "transport":

                        this.connectTransport()

                        break
                }

            },

            this.reconnectDelayMs
        )
    }

    // =====================================================
    // History
    // =====================================================

    private appendHistory(

        channel:
            RuntimeEventType,

        event:
            RuntimeSocketEvent

    ): void {

        let target:
            RuntimeSocketEvent[]

        switch (channel) {

            case "runtime":

                target =
                    this.state
                        .runtimeHistory

                break

            case "replay":

                target =
                    this.state
                        .replayHistory

                break

            case "graph":

                target =
                    this.state
                        .graphHistory

                break

            case "transport":

                target =
                    this.state
                        .transportHistory

                break

            default:

                return
        }

        target.push(event)

        if (
            target.length
            > this.maxHistory
        ) {

            target.splice(

                0,

                target.length
                - this.maxHistory
            )
        }
    }

    // =====================================================
    // Dispatch
    // =====================================================

    private dispatchEvent(
        event: RuntimeSocketEvent
    ): void {

        const listeners =
            this.listeners.get(
                event.event_type
            )

        if (!listeners) {

            return
        }

        for (
            const listener
            of listeners
        ) {

            try {

                listener(event)

            } catch (error) {

                console.error(

                    "[RuntimeSocketManager] listener failure",

                    error
                )
            }
        }
    }

    // =====================================================
    // Subscribe
    // =====================================================

    public subscribe(

        eventType:
            RuntimeEventType,

        listener:
            RuntimeSocketListener

    ): () => void {

        if (
            !this.listeners.has(
                eventType
            )
        ) {

            this.listeners.set(

                eventType,

                new Set()
            )
        }

        this.listeners
            .get(eventType)
            ?.add(listener)

        return () => {

            this.listeners
                .get(eventType)
                ?.delete(listener)
        }
    }

    // =====================================================
    // Shutdown
    // =====================================================

    public shutdown():
        void {

        this.shutdownRequested = true

        this.runtimeSocket?.close()

        this.replaySocket?.close()

        this.graphSocket?.close()

        this.transportSocket?.close()

        this.state.runtimeConnected =
            false

        this.state.replayConnected =
            false

        this.state.graphConnected =
            false

        this.state.transportConnected =
            false
    }

    // =====================================================
    // Metrics
    // =====================================================

    public getMetrics():
        object {

        return {

            runtimeConnected:
                this.state
                    .runtimeConnected,

            replayConnected:
                this.state
                    .replayConnected,

            graphConnected:
                this.state
                    .graphConnected,

            transportConnected:
                this.state
                    .transportConnected,

            runtimeEvents:
                this.state
                    .runtimeHistory
                    .length,

            replayEvents:
                this.state
                    .replayHistory
                    .length,

            graphEvents:
                this.state
                    .graphHistory
                    .length,

            transportEvents:
                this.state
                    .transportHistory
                    .length,

            totalEvents:
                this.state
                    .totalEvents
        }
    }

    // =====================================================
    // Helpers
    // =====================================================

    private toSocketURL(
        endpoint: string
    ): string {

        const protocol =

            window.location.protocol
                === "https:"
                    ? "wss:"
                    : "ws:"

        if (
            endpoint.startsWith(
                "ws://"
            )
            ||
            endpoint.startsWith(
                "wss://"
            )
        ) {

            return endpoint
        }

        return (

            `${protocol}//`

            +

            `${window.location.host}`

            +

            endpoint
        )
    }
}