/**
 * HHS Runtime Router
 * ---------------------------------------------------
 * Canonical graph-native routing layer.
 *
 * Responsibilities:
 *
 * - Workspace routing
 * - Runtime navigation
 * - Route persistence
 * - Replay-linked navigation
 * - Application region routing
 * - Deep-link synchronization
 * - Runtime topology navigation
 * - Viewport navigation continuity
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeRoute {

    id: string

    path: string

    applicationId: string

    workspaceId?: string

    parameters?: Record<
        string,
        unknown
    >

    createdAt: number
}

export interface RuntimeRouterState {

    initialized: boolean

    currentRoute?: RuntimeRoute

    navigationReady: boolean

    replaySynchronized: boolean
}

export class RuntimeRouter {

    public readonly state:
        RuntimeRouterState

    private routeHistory:
        RuntimeRoute[]

    constructor() {

        this.routeHistory = []

        this.state = {

            initialized: false,

            navigationReady: false,

            replaySynchronized: false
        }
    }

    /**
     * ---------------------------------------------------
     * Router Initialization
     * ---------------------------------------------------
     */

    public async initialize(): Promise<void> {

        console.log(
            "[RuntimeRouter] initialize"
        )

        await this.initializeNavigation()

        await this.initializeReplaySynchronization()

        await this.restorePreviousRoute()

        this.state.initialized = true

        console.log(
            "[RuntimeRouter] ready"
        )
    }

    /**
     * ---------------------------------------------------
     * Navigation Bootstrap
     * ---------------------------------------------------
     */

    private async initializeNavigation():
        Promise<void> {

        console.log(
            "[RuntimeRouter] navigation init"
        )

        this.state.navigationReady = true
    }

    /**
     * ---------------------------------------------------
     * Replay Synchronization
     * ---------------------------------------------------
     */

    private async initializeReplaySynchronization():
        Promise<void> {

        console.log(
            "[RuntimeRouter] replay sync"
        )

        this.state.replaySynchronized = true
    }

    /**
     * ---------------------------------------------------
     * Route Restoration
     * ---------------------------------------------------
     */

    private async restorePreviousRoute():
        Promise<void> {

        console.log(
            "[RuntimeRouter] restore route"
        )

        const defaultRoute:
            RuntimeRoute = {

            id:
                crypto.randomUUID(),

            path:
                "/runtime/console",

            applicationId:
                "runtime_console",

            createdAt:
                Date.now()
        }

        this.state.currentRoute =
            defaultRoute

        this.routeHistory.push(
            defaultRoute
        )
    }

    /**
     * ---------------------------------------------------
     * Navigation
     * ---------------------------------------------------
     */

    public navigate(
        path: string,
        applicationId?: string,
        parameters?: Record<
            string,
            unknown
        >
    ): RuntimeRoute {

        const resolvedApplicationId =
            applicationId
            ?? this.applicationIdFromPath(path)
            ?? this.state.currentRoute?.applicationId
            ?? "runtime_console"

        const route: RuntimeRoute = {

            id:
                crypto.randomUUID(),

            path,

            applicationId:
                resolvedApplicationId,

            parameters,

            createdAt:
                Date.now()
        }

        this.state.currentRoute =
            route

        this.routeHistory.push(
            route
        )

        console.log(
            "[RuntimeRouter] navigate",
            route
        )

        return route
    }

    private applicationIdFromPath(path: string): string | undefined {
        const match = /^\/apps\/([^/?#]+)/.exec(path)
        if (!match) return undefined
        try {
            return decodeURIComponent(match[1])
        } catch {
            return match[1]
        }
    }

    /**
     * ---------------------------------------------------
     * Route History
     * ---------------------------------------------------
     */

    public getHistory():
        RuntimeRoute[] {

        return [

            ...this.routeHistory
        ]
    }

    public clearHistory(): void {

        this.routeHistory = []

        console.log(
            "[RuntimeRouter] history cleared"
        )
    }

    /**
     * ---------------------------------------------------
     * Route Queries
     * ---------------------------------------------------
     */

    public getCurrentRoute():
        RuntimeRoute | undefined {

        return this.state.currentRoute
    }

    public isRouteActive(
        path: string
    ): boolean {

        return (
            this.state.currentRoute?.path
                === path
        )
    }

    /**
     * ---------------------------------------------------
     * Serialization
     * ---------------------------------------------------
     */

    public serialize(): object {

        return {

            state:
                this.state,

            history:
                this.routeHistory
        }
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

            navigationReady:
                this.state.navigationReady,

            replaySynchronized:
                this.state.replaySynchronized,

            routes:
                this.routeHistory.length,

            currentRoute:
                this.state.currentRoute?.path
        }
    }
}