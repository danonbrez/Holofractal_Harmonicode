/**
 * =========================================================
 * RuntimeOS
 * =========================================================
 *
 * Canonical Runtime OS orchestration layer.
 *
 * IMPORTANT
 * ---------------------------------------------------------
 * RuntimeOS is NOT runtime authority.
 *
 * Runtime authority belongs to:
 *
 *   - backend runtime
 *   - runtime_event_schema.py
 *   - runtime_ws.py
 *   - replay lineage
 *   - receipt continuity
 *
 * RuntimeOS only:
 *
 *   - orchestrates
 *   - subscribes
 *   - routes
 *   - visualizes
 *   - caches
 *
 * NEVER derive runtime truth here.
 */

import {
    RuntimeSocketManager,
    RuntimeSocketEvent
} from "./RuntimeSocketManager"

import {
    RuntimeStateStore
} from "./RuntimeStateStore"

import {
    runtimeApplicationRegistry
} from "./RuntimeApplicationRegistry"

import {
    RuntimeWindowManager
} from "./RuntimeWindowManager"

// =========================================================
// Config
// =========================================================

export interface RuntimeOSConfig {

    runtimeEndpoint: string

    replayEndpoint: string

    graphEndpoint: string

    transportEndpoint: string
}

// =========================================================
// RuntimeOS
// =========================================================

export class RuntimeOS {

    // =====================================================
    // Core
    // =====================================================

    public readonly socketManager:
        RuntimeSocketManager

    public readonly store:
        RuntimeStateStore

    public readonly registry =
        runtimeApplicationRegistry

    public readonly windowManager:
        RuntimeWindowManager

    // =====================================================
    // Runtime State
    // =====================================================

    private initialized =
        false

    private destroyed =
        false

    private readonly subscriptions:
        (() => void)[] = []

    // =====================================================
    // Constructor
    // =====================================================

    constructor(
        config: RuntimeOSConfig
    ) {

        this.socketManager =
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

        this.windowManager =
            new RuntimeWindowManager()
    }

    // =====================================================
    // Initialize
    // =====================================================

    public async initialize():
        Promise<void> {

        if (
            this.initialized
        ) {

            return
        }

        console.log(
            "[RuntimeOS] initialize"
        )

        // -------------------------------------------------
        // Socket Init
        // -------------------------------------------------

        await this.socketManager.initialize()

        // -------------------------------------------------
        // Runtime Events
        // -------------------------------------------------

        this.subscriptions.push(

            this.socketManager.subscribe(

                "runtime",

                (
                    event:
                        RuntimeSocketEvent
                ) => {

                    this.store.ingestEvent(
                        event
                    )
                }
            )
        )

        // -------------------------------------------------
        // Replay Events
        // -------------------------------------------------

        this.subscriptions.push(

            this.socketManager.subscribe(

                "replay",

                (
                    event:
                        RuntimeSocketEvent
                ) => {

                    this.store.ingestEvent(
                        event
                    )
                }
            )
        )

        // -------------------------------------------------
        // Graph Events
        // -------------------------------------------------

        this.subscriptions.push(

            this.socketManager.subscribe(

                "graph",

                (
                    event:
                        RuntimeSocketEvent
                ) => {

                    this.store.ingestEvent(
                        event
                    )
                }
            )
        )

        // -------------------------------------------------
        // Transport Events
        // -------------------------------------------------

        this.subscriptions.push(

            this.socketManager.subscribe(

                "transport",

                (
                    event:
                        RuntimeSocketEvent
                ) => {

                    this.store.ingestEvent(
                        event
                    )
                }
            )
        )

        // -------------------------------------------------
        // Default Windows
        // -------------------------------------------------

        this.bootstrapWindows()

        // -------------------------------------------------
        // State
        // -------------------------------------------------

        this.initialized = true

        console.log(
            "[RuntimeOS] initialized"
        )
    }

    // =====================================================
    // Bootstrap Windows
    // =====================================================

    private bootstrapWindows():
        void {

        // -------------------------------------------------
        // Runtime Console
        // -------------------------------------------------

        this.windowManager.openWindow({

            id:
                "runtime_console",

            title:
                "Runtime Console",

            applicationId:
                "runtime_console",

            width: 520,

            height: 420,

            x: 80,

            y: 80
        })

        // -------------------------------------------------
        // Calculator
        // -------------------------------------------------

        this.windowManager.openWindow({

            id:
                "calculator",

            title:
                "Calculator",

            applicationId:
                "calculator",

            width: 900,

            height: 600,

            x: 220,

            y: 120
        })

        // -------------------------------------------------
        // Breadboard
        // -------------------------------------------------

        this.windowManager.openWindow({

            id:
                "breadboard",

            title:
                "Breadboard",

            applicationId:
                "breadboard",

            width: 980,

            height: 640,

            x: 160,

            y: 160
        })
    }

    // =====================================================
    // Open Application
    // =====================================================

    public openApplication(
        applicationId: string
    ): void {

        const definition =

            this.registry.get(
                applicationId
            )

        if (!definition) {

            console.error(

                "[RuntimeOS] missing application",

                applicationId
            )

            return
        }

        const preset =
            definition.windowPreset

        this.windowManager.openWindow({

            id:
                `${applicationId}_${Date.now()}`,

            title:
                definition.title,

            applicationId,

            width:
                preset.width,

            height:
                preset.height,

            x: 140,

            y: 140
        })
    }

    // =====================================================
    // Metrics
    // =====================================================

    public getMetrics() {

        return {

            initialized:
                this.initialized,

            destroyed:
                this.destroyed,

            registry:
                this.registry.metrics(),

            store:
                this.store.getMetrics(),

            sockets:
                this.socketManager.getMetrics(),

            windows:
                this.windowManager
                    .getMetrics()
        }
    }

    // =====================================================
    // Destroy
    // =====================================================

    public destroy():
        void {

        if (
            this.destroyed
        ) {

            return
        }

        console.log(
            "[RuntimeOS] destroy"
        )

        // -------------------------------------------------
        // Subscriptions
        // -------------------------------------------------

        for (
            const unsubscribe
            of this.subscriptions
        ) {

            try {

                unsubscribe()

            } catch (error) {

                console.error(

                    "[RuntimeOS] unsubscribe failure",

                    error
                )
            }
        }

        this.subscriptions.length = 0

        // -------------------------------------------------
        // Socket Shutdown
        // -------------------------------------------------

        this.socketManager.shutdown()

        // -------------------------------------------------
        // State Reset
        // -------------------------------------------------

        this.store.reset()

        // -------------------------------------------------
        // Window Reset
        // -------------------------------------------------

        this.windowManager.reset()

        // -------------------------------------------------
        // State
        // -------------------------------------------------

        this.destroyed = true

        console.log(
            "[RuntimeOS] destroyed"
        )
    }
}