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

import {
    RuntimeWorkspace
} from "./RuntimeWorkspace"

import {
    RuntimeRouter
} from "./RuntimeRouter"

import {
    RuntimeSession
} from "./RuntimeSession"

import {
    RuntimeApplicationRegistry
} from "./RuntimeApplicationRegistry"

import {
    RuntimeSocketManager
} from "./RuntimeSocketManager"

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

    public readonly config:
        RuntimeOSConfig

    public readonly workspace:
        RuntimeWorkspace

    public readonly router:
        RuntimeRouter

    public readonly session:
        RuntimeSession

    public readonly applications:
        RuntimeApplicationRegistry

    public readonly sockets:
        RuntimeSocketManager

    public readonly state:
        RuntimeOSState

    private initializedAt:
        number

    constructor(
        config: RuntimeOSConfig
    ) {

        this.config = config

        this.workspace =
            new RuntimeWorkspace()

        this.router =
            new RuntimeRouter()

        this.session =
            new RuntimeSession()

        this.applications =
            new RuntimeApplicationRegistry()

        this.sockets =
            new RuntimeSocketManager({

                runtimeEndpoint:
                    config.runtimeEndpoint,

                replayEndpoint:
                    config.replayEndpoint,

                graphEndpoint:
                    config.graphEndpoint,

                transportEndpoint:
                    config.transportEndpoint
            })

        this.initializedAt =
            Date.now()

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
     * Runtime Bootstrap
     * ---------------------------------------------------
     */

    public async initialize():
        Promise<void> {

        console.log(
            "[RuntimeOS] bootstrap begin"
        )

        await this.initializeWorkspace()

        await this.initializeRouter()

        await this.initializeSession()

        await this.initializeSockets()

        await this.initializeApplications()

        await this.initializeDiagnostics()

        this.bindSocketState()

        this.state.initialized =
            true

        console.log(
            "[RuntimeOS] bootstrap complete"
        )
    }

    /**
     * ---------------------------------------------------
     * Workspace Initialization
     * ---------------------------------------------------
     */

    private async initializeWorkspace():
        Promise<void> {

        console.log(
            "[RuntimeOS] workspace init"
        )

        await this.workspace.initialize()

        this.state.activeWorkspace =
            this.workspace.id
    }

    /**
     * ---------------------------------------------------
     * Router Initialization
     * ---------------------------------------------------
     */

    private async initializeRouter():
        Promise<void> {

        console.log(
            "[RuntimeOS] router init"
        )

        await this.router.initialize()
    }

    /**
     * ---------------------------------------------------
     * Session Initialization
     * ---------------------------------------------------
     */

    private async initializeSession():
        Promise<void> {

        console.log(
            "[RuntimeOS] session init"
        )

        await this.session.initialize()
    }

    /**
     * ---------------------------------------------------
     * Socket Initialization
     * ---------------------------------------------------
     */

    private async initializeSockets():
        Promise<void> {

        console.log(
            "[RuntimeOS] socket init"
        )

        await this.sockets.initialize()
    }

    /**
     * ---------------------------------------------------
     * Application Registration
     * ---------------------------------------------------
     */

    private async initializeApplications():
        Promise<void> {

        console.log(
            "[RuntimeOS] applications init"
        )

        await this.applications.initialize()

        const defaultApplications = [

            {
                id: "runtime_console",

                title: "Runtime Console",

                runtimeType: "console"
            },

            {
                id: "calculator",

                title: "Calculator",

                runtimeType: "symbolic"
            },

            {
                id: "breadboard",

                title: "Breadboard",

                runtimeType: "transport"
            },

            {
                id: "graph_debugger",

                title: "Graph Debugger",

                runtimeType: "graph"
            },

            {
                id: "tensor_inspector",

                title: "Tensor Inspector",

                runtimeType: "tensor"
            },

            {
                id: "replay_viewer",

                title: "Replay Viewer",

                runtimeType: "replay"
            }
        ]

        for (
            const application
            of defaultApplications
        ) {

            this.applications.register({

                ...application,

                mounted: true,

                initialized: true,

                createdAt:
                    Date.now()
            })
        }

        this.state.applicationsMounted =
            this.applications
                .getAll()
                .length
    }

    /**
     * ---------------------------------------------------
     * Diagnostics
     * ---------------------------------------------------
     */

    private async initializeDiagnostics():
        Promise<void> {

        if (
            !this.config
                .diagnosticsEnabled
        ) {

            return
        }

        console.log(
            "[RuntimeOS] diagnostics init"
        )
    }

    /**
     * ---------------------------------------------------
     * Socket State Binding
     * ---------------------------------------------------
     */

    private bindSocketState():
        void {

        this.state.connected =
            this.sockets.state
                .runtimeConnected

        this.state.replayReady =
            this.sockets.state
                .replayConnected

        this.state.graphReady =
            this.sockets.state
                .graphConnected

        this.state.transportReady =
            this.sockets.state
                .transportConnected
    }

    /**
     * ---------------------------------------------------
     * Runtime Shutdown
     * ---------------------------------------------------
     */

    public async shutdown():
        Promise<void> {

        console.log(
            "[RuntimeOS] shutdown begin"
        )

        this.sockets.shutdown()

        this.session.terminate()

        this.state.connected =
            false

        this.state.initialized =
            false

        console.log(
            "[RuntimeOS] shutdown complete"
        )
    }

    /**
     * ---------------------------------------------------
     * Metrics
     * ---------------------------------------------------
     */

    public getMetrics():
        object {

        return {

            uptimeMs:
                Date.now()
                - this.initializedAt,

            applicationsMounted:
                this.state
                    .applicationsMounted,

            replayReady:
                this.state.replayReady,

            graphReady:
                this.state.graphReady,

            transportReady:
                this.state.transportReady,

            connected:
                this.state.connected,

            workspace:
                this.workspace
                    .getMetrics(),

            router:
                this.router
                    .getMetrics(),

            session:
                this.session
                    .getMetrics(),

            applications:
                this.applications
                    .getMetrics(),

            sockets:
                this.sockets
                    .getMetrics()
        }
    }
}