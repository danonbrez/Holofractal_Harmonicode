/**
 * HHS Runtime OS
 * ---------------------------------------------------
 * Canonical Runtime OS orchestration root.
 *
 * Responsibilities:
 *
 * - Runtime bootstrap
 * - ECS initialization
 * - Graph synchronization
 * - Replay synchronization
 * - Runtime transport bootstrap
 * - Multimodal projection initialization
 * - Runtime application registration
 * - Diagnostics orchestration
 * - Websocket stream orchestration
 * - Session continuity
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

import { RuntimeWorkspace } from "./RuntimeWorkspace"
import { RuntimeRouter } from "./RuntimeRouter"
import { RuntimeSession } from "./RuntimeSession"

export interface RuntimeOSConfig {

    runtimeEndpoint: string

    replayEndpoint: string

    graphEndpoint: string

    transportEndpoint: string

    diagnosticsEnabled?: boolean

    mobileMode?: boolean
}

export interface RuntimeOSState {

    initialized: boolean

    connected: boolean

    replayReady: boolean

    graphReady: boolean

    transportReady: boolean

    applicationsMounted: number

    activeWorkspace?: string
}

export class RuntimeOS {

    public readonly config: RuntimeOSConfig

    public readonly workspace: RuntimeWorkspace

    public readonly router: RuntimeRouter

    public readonly session: RuntimeSession

    public readonly state: RuntimeOSState

    private runtimeSocket?: WebSocket

    private replaySocket?: WebSocket

    private graphSocket?: WebSocket

    private transportSocket?: WebSocket

    private applicationRegistry: Map<string, unknown>

    private initializedAt: number

    constructor(config: RuntimeOSConfig) {

        this.config = config

        this.workspace = new RuntimeWorkspace()

        this.router = new RuntimeRouter()

        this.session = new RuntimeSession()

        this.applicationRegistry = new Map()

        this.initializedAt = Date.now()

        this.state = {

            initialized: false,

            connected: false,

            replayReady: false,

            graphReady: false,

            transportReady: false,

            applicationsMounted: 0
        }
    }

    /**
     * ---------------------------------------------------
     * Runtime OS Bootstrap
     * ---------------------------------------------------
     */

    public async initialize(): Promise<void> {

        console.log("[RuntimeOS] bootstrap begin")

        await this.initializeWorkspace()

        await this.initializeSession()

        await this.initializeRuntimeStreams()

        await this.initializeReplay()

        await this.initializeGraph()

        await this.initializeTransport()

        await this.initializeApplications()

        await this.initializeDiagnostics()

        this.state.initialized = true

        console.log("[RuntimeOS] bootstrap complete")
    }

    /**
     * ---------------------------------------------------
     * Workspace Initialization
     * ---------------------------------------------------
     */

    private async initializeWorkspace(): Promise<void> {

        console.log("[RuntimeOS] workspace init")

        await this.workspace.initialize()

        this.state.activeWorkspace = this.workspace.id
    }

    /**
     * ---------------------------------------------------
     * Session Initialization
     * ---------------------------------------------------
     */

    private async initializeSession(): Promise<void> {

        console.log("[RuntimeOS] session init")

        await this.session.initialize()
    }

    /**
     * ---------------------------------------------------
     * Runtime Stream Bootstrap
     * ---------------------------------------------------
     */

    private async initializeRuntimeStreams(): Promise<void> {

        console.log("[RuntimeOS] runtime streams init")

        this.runtimeSocket = new WebSocket(
            this.config.runtimeEndpoint
        )

        this.runtimeSocket.onopen = () => {

            console.log("[RuntimeOS] runtime connected")

            this.state.connected = true
        }

        this.runtimeSocket.onmessage = (event) => {

            this.handleRuntimeMessage(event.data)
        }

        this.runtimeSocket.onerror = (error) => {

            console.error("[RuntimeOS] runtime error", error)
        }
    }

    /**
     * ---------------------------------------------------
     * Replay Synchronization
     * ---------------------------------------------------
     */

    private async initializeReplay(): Promise<void> {

        console.log("[RuntimeOS] replay init")

        this.replaySocket = new WebSocket(
            this.config.replayEndpoint
        )

        this.replaySocket.onopen = () => {

            console.log("[RuntimeOS] replay connected")

            this.state.replayReady = true
        }

        this.replaySocket.onmessage = (event) => {

            this.handleReplayMessage(event.data)
        }
    }

    /**
     * ---------------------------------------------------
     * Graph Synchronization
     * ---------------------------------------------------
     */

    private async initializeGraph(): Promise<void> {

        console.log("[RuntimeOS] graph init")

        this.graphSocket = new WebSocket(
            this.config.graphEndpoint
        )

        this.graphSocket.onopen = () => {

            console.log("[RuntimeOS] graph connected")

            this.state.graphReady = true
        }

        this.graphSocket.onmessage = (event) => {

            this.handleGraphMessage(event.data)
        }
    }

    /**
     * ---------------------------------------------------
     * Transport Synchronization
     * ---------------------------------------------------
     */

    private async initializeTransport(): Promise<void> {

        console.log("[RuntimeOS] transport init")

        this.transportSocket = new WebSocket(
            this.config.transportEndpoint
        )

        this.transportSocket.onopen = () => {

            console.log("[RuntimeOS] transport connected")

            this.state.transportReady = true
        }

        this.transportSocket.onmessage = (event) => {

            this.handleTransportMessage(event.data)
        }
    }

    /**
     * ---------------------------------------------------
     * Application Registration
     * ---------------------------------------------------
     */

    private async initializeApplications(): Promise<void> {

        console.log("[RuntimeOS] applications init")

        const defaultApplications = [

            "calculator",

            "tensor_inspector",

            "receipt_replay_viewer",

            "runtime_console",

            "graph_debugger"
        ]

        for (const app of defaultApplications) {

            this.registerApplication(app, {})
        }
    }

    /**
     * ---------------------------------------------------
     * Diagnostics Initialization
     * ---------------------------------------------------
     */

    private async initializeDiagnostics(): Promise<void> {

        if (!this.config.diagnosticsEnabled) {

            return
        }

        console.log("[RuntimeOS] diagnostics init")
    }

    /**
     * ---------------------------------------------------
     * Runtime Message Routing
     * ---------------------------------------------------
     */

    private handleRuntimeMessage(
        payload: unknown
    ): void {

        console.log("[RuntimeOS] runtime message", payload)
    }

    private handleReplayMessage(
        payload: unknown
    ): void {

        console.log("[RuntimeOS] replay message", payload)
    }

    private handleGraphMessage(
        payload: unknown
    ): void {

        console.log("[RuntimeOS] graph message", payload)
    }

    private handleTransportMessage(
        payload: unknown
    ): void {

        console.log("[RuntimeOS] transport message", payload)
    }

    /**
     * ---------------------------------------------------
     * Application Mounting
     * ---------------------------------------------------
     */

    public registerApplication(
        id: string,
        app: unknown
    ): void {

        if (this.applicationRegistry.has(id)) {

            console.warn(
                `[RuntimeOS] application already registered: ${id}`
            )

            return
        }

        this.applicationRegistry.set(id, app)

        this.state.applicationsMounted += 1

        console.log(
            `[RuntimeOS] application mounted: ${id}`
        )
    }

    public unregisterApplication(
        id: string
    ): void {

        if (!this.applicationRegistry.has(id)) {

            return
        }

        this.applicationRegistry.delete(id)

        this.state.applicationsMounted -= 1

        console.log(
            `[RuntimeOS] application unmounted: ${id}`
        )
    }

    /**
     * ---------------------------------------------------
     * Runtime Shutdown
     * ---------------------------------------------------
     */

    public async shutdown(): Promise<void> {

        console.log("[RuntimeOS] shutdown begin")

        this.runtimeSocket?.close()

        this.replaySocket?.close()

        this.graphSocket?.close()

        this.transportSocket?.close()

        this.state.connected = false

        this.state.initialized = false

        console.log("[RuntimeOS] shutdown complete")
    }

    /**
     * ---------------------------------------------------
     * Runtime Metrics
     * ---------------------------------------------------
     */

    public getMetrics(): object {

        return {

            uptimeMs:
                Date.now() - this.initializedAt,

            applicationsMounted:
                this.state.applicationsMounted,

            replayReady:
                this.state.replayReady,

            graphReady:
                this.state.graphReady,

            transportReady:
                this.state.transportReady,

            connected:
                this.state.connected
        }
    }
}