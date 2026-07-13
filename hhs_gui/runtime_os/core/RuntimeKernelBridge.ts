/**
 * HHS Runtime Kernel Bridge
 * ---------------------------------------------------
 * Canonical Runtime OS <-> HHS runtime bridge layer.
 *
 * Responsibilities:
 *
 * - Runtime kernel transport
 * - WebSocket runtime synchronization
 * - Receipt-stream continuity
 * - Runtime command execution
 * - Deterministic replay transport
 * - Runtime telemetry ingestion
 * - Graph synchronization
 * - Runtime execution orchestration
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

import {
    unwrapRuntimePacketEnvelope,
    validateRuntimeContract
} from "./RuntimeContractEnvelope"

export interface RuntimeKernelBridgeConfig {

    websocketUrl: string

    reconnectIntervalMs?: number

    telemetryIntervalMs?: number

    apiBaseUrl?: string
}

export interface RuntimeKernelReceipt {

    receiptHash?: string

    previousReceipt?: string

    operation?: string

    status?: string

    timestamp?: number

    payload?: object
}

export interface RuntimeKernelTelemetry {

    runtimeFps?: number

    memoryUsage?: number

    activeGraphs?: number

    activeWindows?: number

    replayDepth?: number

    receiptCount?: number
}

export interface RuntimeServiceDispatchPayload {

    service: string

    payload?: Record<string, unknown>
}

export interface RuntimeSRCGSelfSolvePayload {

    A: number

    B: number

    learning_rate?: number

    drift_threshold?: number

    max_steps?: number

    quartic_carrier?: unknown

    proposition?: string
}

export interface RuntimeKernelBridgeState {

    initialized: boolean

    connected: boolean

    connecting: boolean

    replaySynchronized: boolean

    lastReceipt?: string

    lastContractHash72?: string

    lastContractValid?: boolean

    lastContractReasons?: string[]

    telemetry?: RuntimeKernelTelemetry
}

type RuntimeKernelEventCallback =
    (payload: any) => void

export class RuntimeKernelBridge {

    private readonly config:
        RuntimeKernelBridgeConfig

    private websocket?: WebSocket

    private reconnectTimer?: number

    private readonly listeners:
        Map<string, RuntimeKernelEventCallback[]>

    public readonly state:
        RuntimeKernelBridgeState

    constructor(
        config: RuntimeKernelBridgeConfig
    ) {

        this.config = config

        this.listeners = new Map()

        this.state = {

            initialized: false,

            connected: false,

            connecting: false,

            replaySynchronized: false
        }
    }

    /**
     * ---------------------------------------------------
     * Initialization
     * ---------------------------------------------------
     */

    public async initialize():
        Promise<void> {

        console.log(
            "[RuntimeKernelBridge] initialize"
        )

        await this.connect()

        this.state.initialized = true

        console.log(
            "[RuntimeKernelBridge] ready"
        )
    }

    /**
     * ---------------------------------------------------
     * WebSocket Connection
     * ---------------------------------------------------
     */

    public async connect():
        Promise<void> {

        if (
            this.state.connected ||
            this.state.connecting
        ) {

            return
        }

        this.state.connecting = true

        console.log(
            "[RuntimeKernelBridge] connect",
            this.config.websocketUrl
        )

        this.websocket = new WebSocket(

            this.config.websocketUrl
        )

        this.websocket.onopen = () => {

            console.log(
                "[RuntimeKernelBridge] connected"
            )

            this.state.connected = true

            this.state.connecting = false

            this.state.replaySynchronized = true

            this.emit(
                "connected",
                {}
            )
        }

        this.websocket.onmessage = (
            event
        ) => {

            this.handleMessage(
                event.data
            )
        }

        this.websocket.onerror = (
            error
        ) => {

            console.error(
                "[RuntimeKernelBridge] websocket error",
                error
            )
        }

        this.websocket.onclose = () => {

            console.warn(
                "[RuntimeKernelBridge] disconnected"
            )

            this.state.connected = false

            this.state.connecting = false

            this.scheduleReconnect()

            this.emit(
                "disconnected",
                {}
            )
        }
    }

    /**
     * ---------------------------------------------------
     * Reconnect
     * ---------------------------------------------------
     */

    private scheduleReconnect():
        void {

        if (this.reconnectTimer) {

            window.clearTimeout(
                this.reconnectTimer
            )
        }

        this.reconnectTimer =
            window.setTimeout(

                () => {

                    this.connect()

                },

                this.config
                    .reconnectIntervalMs ??
                    3000
            )
    }

    /**
     * ---------------------------------------------------
     * Message Handling
     * ---------------------------------------------------
     */

    private handleMessage(
        raw: string
    ): void {

        try {

            const message =
                JSON.parse(raw)

            const contractEnvelope =
                unwrapRuntimePacketEnvelope(message)

            if (
                message.runtime_contract
            ) {

                const apiValidation =
                    validateRuntimeContract(
                        message.runtime_contract,
                        "api_response"
                    )

                this.state.lastContractValid =
                    apiValidation.ok

                this.state.lastContractReasons =
                    apiValidation.reasons

                if (
                    typeof message.runtime_contract.contract_hash72
                    === "string"
                ) {

                    this.state.lastContractHash72 =
                        message.runtime_contract.contract_hash72
                }
            }

            if (
                contractEnvelope.runtime_packet
            ) {

                this.state.lastContractValid =
                    contractEnvelope.contract_valid

                this.state.lastContractReasons =
                    contractEnvelope.reasons

                if (
                    typeof contractEnvelope.runtime_packet.contract_hash72
                    === "string"
                ) {

                    this.state.lastContractHash72 =
                        contractEnvelope.runtime_packet.contract_hash72
                }
            }

            const type =
                message.type ??
                message.event_type ??
                contractEnvelope.runtime_packet?.source ??
                "runtime_event"

            switch (type) {

                case "receipt":

                    this.handleReceipt(
                        message.payload
                    )

                    break

                case "telemetry":

                    this.handleTelemetry(
                        message.payload
                    )

                    break

                case "graph_update":

                    this.emit(

                        "graph_update",

                        message.payload
                    )

                    break

                case "runtime_event":

                    this.emit(

                        "runtime_event",

                        message.payload
                    )

                    break

                default:

                    console.warn(

                        "[RuntimeKernelBridge] unknown event",

                        type
                    )
            }

        } catch (error) {

            console.error(
                "[RuntimeKernelBridge] parse failure",
                error
            )
        }
    }

    /**
     * ---------------------------------------------------
     * Receipt Handling
     * ---------------------------------------------------
     */

    private handleReceipt(
        receipt:
            RuntimeKernelReceipt
    ): void {

        this.state.lastReceipt =
            receipt.receiptHash

        this.emit(
            "receipt",
            receipt
        )

        console.log(
            "[RuntimeKernelBridge] receipt",
            receipt.receiptHash
        )
    }

    /**
     * ---------------------------------------------------
     * Telemetry Handling
     * ---------------------------------------------------
     */

    private handleTelemetry(
        telemetry:
            RuntimeKernelTelemetry
    ): void {

        this.state.telemetry =
            telemetry

        this.emit(
            "telemetry",
            telemetry
        )
    }

    /**
     * ---------------------------------------------------
     * Runtime Command Dispatch
     * ---------------------------------------------------
     */

    public dispatchCommand(
        operation: string,
        payload?: object
    ): void {

        if (
            !this.websocket ||

            this.websocket.readyState !==
                WebSocket.OPEN
        ) {

            console.warn(
                "[RuntimeKernelBridge] websocket unavailable"
            )

            return
        }

        const message = {

            type: "runtime_command",

            timestamp: Date.now(),

            operation,

            payload
        }

        this.websocket.send(

            JSON.stringify(message)
        )

        console.log(
            "[RuntimeKernelBridge] dispatch",
            operation
        )
    }

    /**
     * ---------------------------------------------------
     * Runtime Execution
     * ---------------------------------------------------
     */

    public executeProgram(
        program: string
    ): void {

        this.dispatchCommand(

            "execute_program",

            {

                program
            }
        )
    }

    public requestReplay(
        receiptHash: string
    ): void {

        this.dispatchCommand(

            "request_replay",

            {

                receiptHash
            }
        )
    }

    public requestTelemetry():
        void {

        this.dispatchCommand(

            "request_telemetry"
        )
    }

    /**
     * ---------------------------------------------------
     * Canonical API Dispatch
     * ---------------------------------------------------
     */

    private apiUrl(
        path: string
    ): string {

        const base =
            this.config.apiBaseUrl ??
            ""

        return `${base}${path}`
    }

    private async postContractAPI(
        path: string,
        payload: object
    ): Promise<any> {

        const response =
            await fetch(
                this.apiUrl(path),
                {
                    method: "POST",
                    headers: {
                        "content-type": "application/json"
                    },
                    body: JSON.stringify(payload)
                }
            )

        const envelope =
            await response.json()

        if (
            envelope.runtime_contract
        ) {

            const validation =
                validateRuntimeContract(
                    envelope.runtime_contract,
                    "api_response"
                )

            this.state.lastContractValid =
                validation.ok

            this.state.lastContractReasons =
                validation.reasons

            if (
                typeof envelope.runtime_contract.contract_hash72
                === "string"
            ) {

                this.state.lastContractHash72 =
                    envelope.runtime_contract.contract_hash72
            }
        }

        if (!response.ok) {

            throw new Error(
                `runtime_api_error:${response.status}`
            )
        }

        return envelope
    }

    public async dispatchService(
        service: string,
        payload?: Record<string, unknown>
    ): Promise<any> {

        return this.postContractAPI(
            "/api/runtime/services/dispatch",
            {
                service,
                payload: payload ?? {}
            }
        )
    }

    public async executeSRCGSelfSolve(
        payload: RuntimeSRCGSelfSolvePayload
    ): Promise<any> {

        return this.postContractAPI(
            "/api/runtime/srcg/selfsolve",
            payload
        )
    }

    /**
     * ---------------------------------------------------
     * Event Subscription
     * ---------------------------------------------------
     */

    public on(
        event: string,
        callback:
            RuntimeKernelEventCallback
    ): void {

        const existing =
            this.listeners.get(event)

        if (!existing) {

            this.listeners.set(

                event,

                [callback]
            )

            return
        }

        existing.push(callback)
    }

    public off(
        event: string,
        callback:
            RuntimeKernelEventCallback
    ): void {

        const existing =
            this.listeners.get(event)

        if (!existing) {

            return
        }

        this.listeners.set(

            event,

            existing.filter(

                (candidate) =>
                    candidate !== callback
            )
        )
    }

    private emit(
        event: string,
        payload: any
    ): void {

        const listeners =
            this.listeners.get(event)

        if (!listeners) {

            return
        }

        for (
            const listener
            of listeners
        ) {

            listener(payload)
        }
    }

    /**
     * ---------------------------------------------------
     * Disconnect
     * ---------------------------------------------------
     */

    public disconnect():
        void {

        if (this.websocket) {

            this.websocket.close()
        }

        this.state.connected = false
    }

    /**
     * ---------------------------------------------------
     * Metrics
     * ---------------------------------------------------
     */

    public getMetrics(): object {

        return {

            initialized:
                this.state.initialized,

            connected:
                this.state.connected,

            replaySynchronized:
                this.state.replaySynchronized,

            lastReceipt:
                this.state.lastReceipt,

            lastContractHash72:
                this.state.lastContractHash72,

            lastContractValid:
                this.state.lastContractValid,

            lastContractReasons:
                this.state.lastContractReasons,

            telemetry:
                this.state.telemetry
        }
    }

    /**
     * ---------------------------------------------------
     * Serialization
     * ---------------------------------------------------
     */

    public serialize(): object {

        return {

            config:
                this.config,

            state:
                this.state
        }
    }
}