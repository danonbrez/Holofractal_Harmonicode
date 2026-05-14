/**
 * =========================================================
 * RuntimeOS
 * =========================================================
 *
 * Canonical frontend Runtime OS authority.
 *
 * Responsibilities:
 *
 * - Runtime bootstrap
 * - Workspace orchestration
 * - RuntimeSocketManager lifecycle
 * - RuntimeStateStore synchronization
 * - Application registry
 * - Runtime metrics
 * - Projection state
 * - Window topology
 */

import {
    RuntimeSocketManager
} from "./RuntimeSocketManager"

import type {
    RuntimeSocketEvent
} from "./RuntimeSocketManager"

import {
    RuntimeStateStore
} from "../state/RuntimeStateStore"

// =========================================================
// Workspace Types
// =========================================================

export interface RuntimeWindow {

    id: string

    title: string

    applicationId: string

    x: number

    y: number

    width: number

    height: number

    minimized: boolean

    maximized: boolean

    focused: boolean
}

// ---------------------------------------------------------

export interface RuntimeWorkspaceLayout {

    windows: RuntimeWindow[]
}

// ---------------------------------------------------------

export interface RuntimeWorkspace {

    id: string

    layout: RuntimeWorkspaceLayout
}

// =========================================================
// RuntimeOS Config
// =========================================================

export interface RuntimeOSConfig {

    runtimeEndpoint: string

    replayEndpoint: string

    graphEndpoint: string

    transportEndpoint: string

    diagnosticsEnabled?: boolean

    mobileMode?: boolean
}

// =========================================================
// RuntimeOS State
// =========================================================

export interface RuntimeOSState {

    initialized: boolean

    booted: boolean

    connected: boolean

    replayReady: boolean

    graphReady: boolean

    transportReady: boolean

    diagnosticsEnabled: boolean

    mobileMode: boolean

    applicationsMounted: number

    totalEvents: number

    uptimeStartedAt: number
}

// =========================================================
// RuntimeOS
// =========================================================

export class RuntimeOS {

    public readonly config:
        RuntimeOSConfig

    public readonly sockets:
        RuntimeSocketManager

    public readonly store:
        RuntimeStateStore

    public readonly workspace:
        RuntimeWorkspace

    public readonly state:
        RuntimeOSState

    // =====================================================
    // Constructor
    // =====================================================

    constructor(
        config: RuntimeOSConfig
    ) {

        this.config = config

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

        this.store =
            new RuntimeStateStore()

        this.workspace = {

            id:
                "runtime_workspace",

            layout: {

                windows: [

                    {
                        id:
                            "runtime_console_window",

                        title:
                            "Runtime Console",

                        applicationId:
                            "runtime_console",

                        x: 40,

                        y: 60,

                        width: 520,

                        height: 420,

                        minimized: false,

                        maximized: false,

                        focused: true
                    },

                    {
                        id:
                            "calculator_window",

                        title:
                            "Calculator",

                        applicationId:
                            "calculator",

                        x: 620,

                        y: 80,

                        width: 700,

                        height: 520,

                        minimized: false,

                        maximized: false,

                        focused: false
                    },

                    {
                        id:
                            "breadboard_window",

                        title:
                            "Breadboard",

                        applicationId:
                            "breadboard",

                        x: 240,

                        y: 160,

                        width: 820,

                        height: 520,

                        minimized: false,

                        maximized: false,

                        focused: false
                    }
                ]
            }
        }

        this.state = {

            initialized: false,

            booted: false,

            connected: false,

            replayReady: false,

            graphReady: false,

            transportReady: false,

            diagnosticsEnabled:

                config
                    .diagnosticsEnabled
                    ?? false,

            mobileMode:

                config
                    .mobileMode
                    ?? false,

            applicationsMounted:

                this.workspace
                    .layout
                    .windows
                    .length,

            totalEvents: 0,

            uptimeStartedAt:
                performance.now()
        }
    }

    // =====================================================
    // Initialize
    // =====================================================

    public async initialize():
        Promise<void> {

        if (
            this.state.initialized
        ) {

            return
        }

        this.state.initialized =
            true

        this.bindSocketEvents()

        await this.sockets.initialize()

        this.state.booted =
            true

        console.log(
            "[RuntimeOS] initialized"
        )
    }

    // =====================================================
    // Socket Binding
    // =====================================================

    private bindSocketEvents():
        void {

        this.sockets.subscribe(

            "runtime",

            (
                event
            ) => {

                this.handleRuntimeEvent(
                    event
                )
            }
        )

        this.sockets.subscribe(

            "replay",

            (
                event
            ) => {

                this.handleReplayEvent(
                    event
                )
            }
        )

        this.sockets.subscribe(

            "graph",

            (
                event
            ) => {

                this.handleGraphEvent(
                    event
                )
            }
        )

        this.sockets.subscribe(

            "transport",

            (
                event
            ) => {

                this.handleTransportEvent(
                    event
                )
            }
        )

        this.sockets.subscribe(

            "receipt",

            (
                event
            ) => {

                this.handleReceiptEvent(
                    event
                )
            }
        )
    }

    // =====================================================
    // Event Handlers
    // =====================================================

    private handleRuntimeEvent(
        event: RuntimeSocketEvent
    ): void {

        this.store.ingestEvent(
            event
        )

        this.state.connected =
            true

        this.state.totalEvents += 1
    }

    // -----------------------------------------------------

    private handleReplayEvent(
        event: RuntimeSocketEvent
    ): void {

        this.store.ingestEvent(
            event
        )

        this.state.replayReady =
            true

        this.state.totalEvents += 1
    }

    // -----------------------------------------------------

    private handleGraphEvent(
        event: RuntimeSocketEvent
    ): void {

        this.store.ingestEvent(
            event
        )

        this.state.graphReady =
            true

        this.state.totalEvents += 1
    }

    // -----------------------------------------------------

    private handleTransportEvent(
        event: RuntimeSocketEvent
    ): void {

        this.store.ingestEvent(
            event
        )

        this.state.transportReady =
            true

        this.state.totalEvents += 1
    }

    // -----------------------------------------------------

    private handleReceiptEvent(
        event: RuntimeSocketEvent
    ): void {

        this.store.ingestEvent(
            event
        )

        this.state.totalEvents += 1
    }

    // =====================================================
    // Windows
    // =====================================================

    public focusWindow(
        windowId: string
    ): void {

        for (
            const window
            of this.workspace
                .layout
                .windows
        ) {

            window.focused =
                (
                    window.id
                    === windowId
                )
        }
    }

    // -----------------------------------------------------

    public minimizeWindow(
        windowId: string
    ): void {

        const target =
            this.workspace
                .layout
                .windows
                .find(

                    (
                        window
                    ) => (

                        window.id
                        === windowId
                    )
                )

        if (!target) {

            return
        }

        target.minimized =
            !target.minimized
    }

    // -----------------------------------------------------

    public maximizeWindow(
        windowId: string
    ): void {

        const target =
            this.workspace
                .layout
                .windows
                .find(

                    (
                        window
                    ) => (

                        window.id
                        === windowId
                    )
                )

        if (!target) {

            return
        }

        target.maximized =
            !target.maximized
    }

    // =====================================================
    // Metrics
    // =====================================================

    public getMetrics():
        Record<
            string,
            unknown
        > {

        return {

            initialized:
                this.state
                    .initialized,

            booted:
                this.state
                    .booted,

            connected:
                this.state
                    .connected,

            replayReady:
                this.state
                    .replayReady,

            graphReady:
                this.state
                    .graphReady,

            transportReady:
                this.state
                    .transportReady,

            diagnosticsEnabled:
                this.state
                    .diagnosticsEnabled,

            mobileMode:
                this.state
                    .mobileMode,

            applicationsMounted:
                this.state
                    .applicationsMounted,

            totalEvents:
                this.state
                    .totalEvents,

            uptimeMs:

                performance.now()

                -

                this.state
                    .uptimeStartedAt,

            sockets:
                this.sockets
                    .getMetrics(),

            runtimeStore:
                this.store
                    .getMetrics(),

            workspaceWindows:

                this.workspace
                    .layout
                    .windows
                    .length
        }
    }

    // =====================================================
    // Shutdown
    // =====================================================

    public shutdown():
        void {

        this.sockets.shutdown()

        this.state.connected =
            false

        this.state.replayReady =
            false

        this.state.graphReady =
            false

        this.state.transportReady =
            false

        console.log(
            "[RuntimeOS] shutdown"
        )
    }
}