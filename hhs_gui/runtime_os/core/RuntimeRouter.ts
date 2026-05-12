/**
 * HHS Runtime Router
 * ---------------------------------------------------
 * Canonical Runtime OS routing and orchestration layer.
 *
 * Responsibilities:
 *
 * - Runtime application routing
 * - Process manifold routing
 * - Workspace navigation
 * - Replay-linked route continuity
 * - Graph-native route topology
 * - Runtime transport routing
 * - Application mounting orchestration
 * - Deep-link replay reconstruction
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeRoute {

    id: string

    route: string

    applicationId: string

    workspaceId?: string

    graphRegion?: string

    replayState?: object

    transportState?: object

    metadata?: object
}

export interface RuntimeNavigationEvent {

    previousRoute?: string

    nextRoute: string

    timestamp: number

    replayLinked: boolean
}

export interface RuntimeRouterState {

    initialized: boolean

    currentRoute?: string

    previousRoute?: string

    navigationCount: number

    replaySynchronized: boolean
}

export class RuntimeRouter {

    private readonly routes:
        Map<string, RuntimeRoute>

    private readonly navigationHistory:
        RuntimeNavigationEvent[]

    public readonly state:
        RuntimeRouterState

    constructor() {

        this.routes = new Map()

        this.navigationHistory = []

        this.state = {

            initialized: false,

            navigationCount: 0,

            replaySynchronized: false
        }

        this.initializeDefaultRoutes()
    }

    /**
     * ---------------------------------------------------
     * Route Bootstrap
     * ---------------------------------------------------
     */

    private initializeDefaultRoutes(): void {

        const defaultRoutes: RuntimeRoute[] = [

            {

                id: crypto.randomUUID(),

                route: "/",

                applicationId:
                    "runtime_console",

                graphRegion:
                    "root_workspace"
            },

            {

                id: crypto.randomUUID(),

                route: "/calculator",

                applicationId:
                    "calculator",

                graphRegion:
                    "symbolic_region"
            },

            {

                id: crypto.randomUUID(),

                route: "/graph",

                applicationId:
                    "graph_debugger",

                graphRegion:
                    "graph_region"
            },

            {

                id: crypto.randomUUID(),

                route: "/tensor",

                applicationId:
                    "tensor_inspector",

                graphRegion:
                    "tensor_region"
            },

            {

                id: crypto.randomUUID(),

                route: "/replay",

                applicationId:
                    "receipt_replay_viewer",

                graphRegion:
                    "replay_region"
            },

            {

                id: crypto.randomUUID(),

                route: "/physics",

                applicationId:
                    "physics_sandbox",

                graphRegion:
                    "simulation_region"
            },

            {

                id: crypto.randomUUID(),

                route: "/breadboard",

                applicationId:
                    "runtime_breadboard",

                graphRegion:
                    "transport_region"
            },

            {

                id: crypto.randomUUID(),

                route: "/ide",

                applicationId:
                    "visual_ide",

                graphRegion:
                    "compiler_region"
            }
        ]

        for (const route of defaultRoutes) {

            this.registerRoute(route)
        }

        this.state.initialized = true

        this.state.replaySynchronized = true
    }

    /**
     * ---------------------------------------------------
     * Route Registration
     * ---------------------------------------------------
     */

    public registerRoute(
        route: RuntimeRoute
    ): void {

        this.routes.set(
            route.route,
            route
        )

        console.log(
            "[RuntimeRouter] route registered",
            route.route
        )
    }

    public unregisterRoute(
        routePath: string
    ): void {

        this.routes.delete(routePath)

        console.log(
            "[RuntimeRouter] route removed",
            routePath
        )
    }

    /**
     * ---------------------------------------------------
     * Navigation
     * ---------------------------------------------------
     */

    public navigate(
        routePath: string
    ): RuntimeRoute | undefined {

        const route =
            this.routes.get(routePath)

        if (!route) {

            console.warn(
                "[RuntimeRouter] route not found",
                routePath
            )

            return undefined
        }

        const navigationEvent:
            RuntimeNavigationEvent = {

            previousRoute:
                this.state.currentRoute,

            nextRoute:
                routePath,

            timestamp:
                Date.now(),

            replayLinked: true
        }

        this.navigationHistory.push(
            navigationEvent
        )

        this.state.previousRoute =
            this.state.currentRoute

        this.state.currentRoute =
            routePath

        this.state.navigationCount += 1

        console.log(
            "[RuntimeRouter] navigate",
            routePath
        )

        return route
    }

    /**
     * ---------------------------------------------------
     * Back Navigation
     * ---------------------------------------------------
     */

    public back():
        RuntimeRoute | undefined {

        if (
            this.navigationHistory.length < 2
        ) {

            return undefined
        }

        /**
         * Remove current event
         */

        this.navigationHistory.pop()

        /**
         * Previous event
         */

        const previousEvent =
            this.navigationHistory[
                this.navigationHistory.length - 1
            ]

        if (!previousEvent) {

            return undefined
        }

        return this.navigate(
            previousEvent.nextRoute
        )
    }

    /**
     * ---------------------------------------------------
     * Route Resolution
     * ---------------------------------------------------
     */

    public resolveRoute(
        routePath: string
    ): RuntimeRoute | undefined {

        return this.routes.get(routePath)
    }

    public getCurrentRoute():
        RuntimeRoute | undefined {

        if (!this.state.currentRoute) {

            return undefined
        }

        return this.routes.get(
            this.state.currentRoute
        )
    }

    public getRoutes():
        RuntimeRoute[] {

        return Array.from(
            this.routes.values()
        )
    }

    /**
     * ---------------------------------------------------
     * Deep-Link Replay Routing
     * ---------------------------------------------------
     */

    public replayNavigate(
        replayId: string
    ): void {

        console.log(
            "[RuntimeRouter] replay navigate",
            replayId
        )

        /**
         * Future:
         * replay reconstruction routing
         * branch restoration
         * graph continuity recovery
         */
    }

    /**
     * ---------------------------------------------------
     * Graph Region Routing
     * ---------------------------------------------------
     */

    public navigateGraphRegion(
        graphRegion: string
    ): RuntimeRoute | undefined {

        const routes =
            this.getRoutes()

        const route = routes.find(

            (candidate) =>
                candidate.graphRegion ===
                graphRegion
        )

        if (!route) {

            return undefined
        }

        return this.navigate(
            route.route
        )
    }

    /**
     * ---------------------------------------------------
     * Serialization
     * ---------------------------------------------------
     */

    public serialize(): object {

        return {

            state: this.state,

            routes:
                this.getRoutes(),

            navigationHistory:
                this.navigationHistory
        }
    }

    /**
     * ---------------------------------------------------
     * Metrics
     * ---------------------------------------------------
     */

    public getMetrics(): object {

        return {

            registeredRoutes:
                this.routes.size,

            currentRoute:
                this.state.currentRoute,

            previousRoute:
                this.state.previousRoute,

            navigationCount:
                this.state.navigationCount,

            replaySynchronized:
                this.state.replaySynchronized
        }
    }
}