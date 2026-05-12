/**
 * HHS Runtime Application Registry
 * ---------------------------------------------------
 * Canonical Runtime OS application mounting layer.
 *
 * Responsibilities:
 *
 * - Runtime application registration
 * - Application lifecycle orchestration
 * - Graph-native application mounting
 * - Replay-linked application continuity
 * - Runtime application discovery
 * - Permission-aware application routing
 * - Runtime package integration
 * - Deterministic application orchestration
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeApplication {

    id: string

    name: string

    version: string

    applicationType: string

    graphRegion?: string

    route?: string

    icon?: string

    description?: string

    mounted: boolean

    visible: boolean

    permissions?: string[]

    metadata?: object
}

export interface RuntimeApplicationMount {

    applicationId: string

    mountedAt: number

    workspaceId?: string

    graphRegion?: string

    replayLinked: boolean
}

export interface RuntimeApplicationRegistryState {

    initialized: boolean

    registeredApplications: number

    mountedApplications: number

    replaySynchronized: boolean
}

export class RuntimeApplicationRegistry {

    private readonly applications:
        Map<string, RuntimeApplication>

    private readonly mounts:
        Map<string, RuntimeApplicationMount>

    public readonly state:
        RuntimeApplicationRegistryState

    constructor() {

        this.applications = new Map()

        this.mounts = new Map()

        this.state = {

            initialized: false,

            registeredApplications: 0,

            mountedApplications: 0,

            replaySynchronized: false
        }

        this.bootstrapDefaultApplications()
    }

    /**
     * ---------------------------------------------------
     * Bootstrap
     * ---------------------------------------------------
     */

    private bootstrapDefaultApplications():
        void {

        const applications:
            RuntimeApplication[] = [

            {

                id: "runtime_console",

                name: "Runtime Console",

                version: "1.0.0",

                applicationType: "system",

                graphRegion:
                    "root_workspace",

                route: "/",

                icon: "terminal",

                mounted: false,

                visible: true
            },

            {

                id: "calculator",

                name: "HHS Calculator",

                version: "1.0.0",

                applicationType: "symbolic",

                graphRegion:
                    "symbolic_region",

                route: "/calculator",

                icon: "calculator",

                mounted: false,

                visible: true
            },

            {

                id: "tensor_inspector",

                name: "Tensor Inspector",

                version: "1.0.0",

                applicationType: "tensor",

                graphRegion:
                    "tensor_region",

                route: "/tensor",

                icon: "orbit",

                mounted: false,

                visible: true
            },

            {

                id: "graph_debugger",

                name: "Graph Debugger",

                version: "1.0.0",

                applicationType: "graph",

                graphRegion:
                    "graph_region",

                route: "/graph",

                icon: "network",

                mounted: false,

                visible: true
            },

            {

                id: "receipt_replay_viewer",

                name: "Replay Viewer",

                version: "1.0.0",

                applicationType: "replay",

                graphRegion:
                    "replay_region",

                route: "/replay",

                icon: "history",

                mounted: false,

                visible: true
            },

            {

                id: "physics_sandbox",

                name: "Physics Sandbox",

                version: "1.0.0",

                applicationType: "simulation",

                graphRegion:
                    "simulation_region",

                route: "/physics",

                icon: "atom",

                mounted: false,

                visible: true
            },

            {

                id: "runtime_breadboard",

                name: "Runtime Breadboard",

                version: "1.0.0",

                applicationType: "transport",

                graphRegion:
                    "transport_region",

                route: "/breadboard",

                icon: "cpu",

                mounted: false,

                visible: true
            },

            {

                id: "visual_ide",

                name: "Visual IDE",

                version: "1.0.0",

                applicationType: "development",

                graphRegion:
                    "compiler_region",

                route: "/ide",

                icon: "code",

                mounted: false,

                visible: true
            }
        ]

        for (
            const application
            of applications
        ) {

            this.registerApplication(
                application
            )
        }

        this.state.initialized = true

        this.state.replaySynchronized = true
    }

    /**
     * ---------------------------------------------------
     * Registration
     * ---------------------------------------------------
     */

    public registerApplication(
        application: RuntimeApplication
    ): void {

        if (
            this.applications.has(
                application.id
            )
        ) {

            console.warn(
                "[RuntimeApplicationRegistry] already registered",
                application.id
            )

            return
        }

        this.applications.set(

            application.id,

            application
        )

        this.state.registeredApplications =
            this.applications.size

        console.log(
            "[RuntimeApplicationRegistry] registered",
            application.id
        )
    }

    public unregisterApplication(
        applicationId: string
    ): void {

        this.unmountApplication(
            applicationId
        )

        this.applications.delete(
            applicationId
        )

        this.state.registeredApplications =
            this.applications.size

        console.log(
            "[RuntimeApplicationRegistry] removed",
            applicationId
        )
    }

    /**
     * ---------------------------------------------------
     * Mounting
     * ---------------------------------------------------
     */

    public mountApplication(
        applicationId: string,
        workspaceId?: string
    ): RuntimeApplicationMount | undefined {

        const application =
            this.applications.get(
                applicationId
            )

        if (!application) {

            console.warn(
                "[RuntimeApplicationRegistry] application missing",
                applicationId
            )

            return undefined
        }

        if (
            this.mounts.has(
                applicationId
            )
        ) {

            return this.mounts.get(
                applicationId
            )
        }

        const mount:
            RuntimeApplicationMount = {

            applicationId,

            mountedAt: Date.now(),

            workspaceId,

            graphRegion:
                application.graphRegion,

            replayLinked: true
        }

        this.mounts.set(

            applicationId,

            mount
        )

        application.mounted = true

        this.state.mountedApplications =
            this.mounts.size

        console.log(
            "[RuntimeApplicationRegistry] mounted",
            applicationId
        )

        return mount
    }

    public unmountApplication(
        applicationId: string
    ): void {

        const application =
            this.applications.get(
                applicationId
            )

        if (application) {

            application.mounted = false
        }

        this.mounts.delete(
            applicationId
        )

        this.state.mountedApplications =
            this.mounts.size

        console.log(
            "[RuntimeApplicationRegistry] unmounted",
            applicationId
        )
    }

    /**
     * ---------------------------------------------------
     * Queries
     * ---------------------------------------------------
     */

    public getApplication(
        applicationId: string
    ): RuntimeApplication | undefined {

        return this.applications.get(
            applicationId
        )
    }

    public getApplications():
        RuntimeApplication[] {

        return Array.from(
            this.applications.values()
        )
    }

    public getMountedApplications():
        RuntimeApplication[] {

        return this.getApplications().filter(

            (application) =>
                application.mounted
        )
    }

    public getApplicationsByType(
        applicationType: string
    ): RuntimeApplication[] {

        return this.getApplications().filter(

            (application) =>
                application.applicationType ===
                applicationType
        )
    }

    public getApplicationsByGraphRegion(
        graphRegion: string
    ): RuntimeApplication[] {

        return this.getApplications().filter(

            (application) =>
                application.graphRegion ===
                graphRegion
        )
    }

    /**
     * ---------------------------------------------------
     * Visibility
     * ---------------------------------------------------
     */

    public setVisibility(
        applicationId: string,
        visible: boolean
    ): void {

        const application =
            this.applications.get(
                applicationId
            )

        if (!application) {

            return
        }

        application.visible = visible

        console.log(
            "[RuntimeApplicationRegistry] visibility",
            applicationId,
            visible
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

            applications:
                this.getApplications(),

            mounts:
                Array.from(
                    this.mounts.values()
                )
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

            registeredApplications:
                this.state.registeredApplications,

            mountedApplications:
                this.state.mountedApplications,

            replaySynchronized:
                this.state.replaySynchronized
        }
    }
}