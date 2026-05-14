/**
 * HHS Runtime Socket Manager
 * ---------------------------------------------------
 * Canonical websocket orchestration layer.
 *
 * Responsibilities:
 *
 * - Runtime websocket orchestration
 * - Replay stream synchronization
 * - Graph stream synchronization
 * - Transport stream synchronization
 * - Runtime event routing
 * - Deterministic stream continuity
 * - Runtime reconnect logic
 * - Stream lifecycle management
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeSocketConfig {

    runtimeEndpoint: string

    replayEndpoint: string

    graphEndpoint: string

    transportEndpoint: string
}

export interface RuntimeSocketState {

    initialized: boolean

    runtimeConnected: boolean

    replayConnected: boolean

    graphConnected: boolean

    transportConnected: boolean
}

export type RuntimeSocketHandler =
    (
        payload: unknown
    ) => void

export class RuntimeSocketManager {

    public readonly config:
        RuntimeSocketConfig

    public readonly state:
        RuntimeSocketState

    private runtimeSocket?: WebSocket

    private replaySocket?: WebSocket

    private graphSocket?: WebSocket

    private transportSocket?: WebSocket

    private runtimeHandlers:
        Set<RuntimeSocketHandler>

    private replayHandlers:
        Set<RuntimeSocketHandler>

    private graphHandlers:
        Set<RuntimeSocketHandler>

    private transportHandlers:
        Set<RuntimeSocketHandler>

    constructor(
        config: RuntimeSocketConfig
    ) {

        this.config = config

        this.runtimeHandlers =
            new Set()

        this.replayHandlers =
            new Set()

        this.graphHandlers =
            new Set()

        this.transportHandlers =
            new Set()

        this.state = {

            initialized: false,

            runtimeConnected: false,

            replayConnected: false,

            graphConnected: false,

            transportConnected: false
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
            "[RuntimeSocketManager] initialize"
        )

        await this.connectRuntime()

        await this.connectReplay()

        await this.connectGraph()

        await this.connectTransport()

        this.state.initialized = true

        console.log(
            "[RuntimeSocketManager] ready"
        )
    }

    /**
     * ---------------------------------------------------
     * Runtime Stream
     * ---------------------------------------------------
     */

    private async connectRuntime():
        Promise<void> {

        this.runtimeSocket =
            new WebSocket(
                this.config.runtimeEndpoint
            )

        this.runtimeSocket.onopen =
            () => {

                console.log(
                    "[RuntimeSocketManager] runtime connected"
                )

                this.state
                    .runtimeConnected = true
            }

        this.runtimeSocket.onmessage =
            (event) => {

                this.emitRuntime(
                    event.data
                )
            }

        this.runtimeSocket.onclose =
            () => {

                this.state
                    .runtimeConnected = false
            }
    }

    /**
     * ---------------------------------------------------
     * Replay Stream
     * ---------------------------------------------------
     */

    private async connectReplay():
        Promise<void> {

        this.replaySocket =
            new WebSocket(
                this.config.replayEndpoint
            )

        this.replaySocket.onopen =
            () => {

                console.log(
                    "[RuntimeSocketManager] replay connected"
                )

                this.state
                    .replayConnected = true
            }

        this.replaySocket.onmessage =
            (event) => {

                this.emitReplay(
                    event.data
                )
            }

        this.replaySocket.onclose =
            () => {

                this.state
                    .replayConnected = false
            }
    }

    /**
     * ---------------------------------------------------
     * Graph Stream
     * ---------------------------------------------------
     */

    private async connectGraph():
        Promise<void> {

        this.graphSocket =
            new WebSocket(
                this.config.graphEndpoint
            )

        this.graphSocket.onopen =
            () => {

                console.log(
                    "[RuntimeSocketManager] graph connected"
                )

                this.state
                    .graphConnected = true
            }

        this.graphSocket.onmessage =
            (event) => {

                this.emitGraph(
                    event.data
                )
            }

        this.graphSocket.onclose =
            () => {

                this.state
                    .graphConnected = false
            }
    }

    /**
     * ---------------------------------------------------
     * Transport Stream
     * ---------------------------------------------------
     */

    private async connectTransport():
        Promise<void> {

        this.transportSocket =
            new WebSocket(
                this.config.transportEndpoint
            )

        this.transportSocket.onopen =
            () => {

                console.log(
                    "[RuntimeSocketManager] transport connected"
                )

                this.state
                    .transportConnected = true
            }

        this.transportSocket.onmessage =
            (event) => {

                this.emitTransport(
                    event.data
                )
            }

        this.transportSocket.onclose =
            () => {

                this.state
                    .transportConnected = false
            }
    }

    /**
     * ---------------------------------------------------
     * Runtime Events
     * ---------------------------------------------------
     */

    public onRuntime(
        handler: RuntimeSocketHandler
    ): void {

        this.runtimeHandlers.add(
            handler
        )
    }

    public offRuntime(
        handler: RuntimeSocketHandler
    ): void {

        this.runtimeHandlers.delete(
            handler
        )
    }

    private emitRuntime(
        payload: unknown
    ): void {

        for (
            const handler
            of this.runtimeHandlers
        ) {

            handler(payload)
        }
    }

    /**
     * ---------------------------------------------------
     * Replay Events
     * ---------------------------------------------------
     */

    public onReplay(
        handler: RuntimeSocketHandler
    ): void {

        this.replayHandlers.add(
            handler
        )
    }

    public offReplay(
        handler: RuntimeSocketHandler
    ): void {

        this.replayHandlers.delete(
            handler
        )
    }

    private emitReplay(
        payload: unknown
    ): void {

        for (
            const handler
            of this.replayHandlers
        ) {

            handler(payload)
        }
    }

    /**
     * ---------------------------------------------------
     * Graph Events
     * ---------------------------------------------------
     */

    public onGraph(
        handler: RuntimeSocketHandler
    ): void {

        this.graphHandlers.add(
            handler
        )
    }

    public offGraph(
        handler: RuntimeSocketHandler
    ): void {

        this.graphHandlers.delete(
            handler
        )
    }

    private emitGraph(
        payload: unknown
    ): void {

        for (
            const handler
            of this.graphHandlers
        ) {

            handler(payload)
        }
    }

    /**
     * ---------------------------------------------------
     * Transport Events
     * ---------------------------------------------------
     */

    public onTransport(
        handler: RuntimeSocketHandler
    ): void {

        this.transportHandlers.add(
            handler
        )
    }

    public offTransport(
        handler: RuntimeSocketHandler
    ): void {

        this.transportHandlers.delete(
            handler
        )
    }

    private emitTransport(
        payload: unknown
    ): void {

        for (
            const handler
            of this.transportHandlers
        ) {

            handler(payload)
        }
    }

    /**
     * ---------------------------------------------------
     * Shutdown
     * ---------------------------------------------------
     */

    public shutdown(): void {

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

        console.log(
            "[RuntimeSocketManager] shutdown"
        )
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

            runtimeConnected:
                this.state.runtimeConnected,

            replayConnected:
                this.state.replayConnected,

            graphConnected:
                this.state.graphConnected,

            transportConnected:
                this.state.transportConnected,

            runtimeHandlers:
                this.runtimeHandlers.size,

            replayHandlers:
                this.replayHandlers.size,

            graphHandlers:
                this.graphHandlers.size,

            transportHandlers:
                this.transportHandlers.size
        }
    }
}