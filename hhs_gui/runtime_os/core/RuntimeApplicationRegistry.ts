/**
 * HHS Runtime Application Registry
 * ---------------------------------------------------
 * Canonical Runtime OS application registry.
 *
 * Responsibilities:
 *
 * - Runtime application registration
 * - Application lifecycle orchestration
 * - Runtime application lookup
 * - Workspace application mounting
 * - Replay-linked application continuity
 * - Runtime application metadata
 * - Graph-native application topology
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeApplication {

    id: string

    title: string

    runtimeType: string

    icon?: string

    mounted: boolean

    initialized: boolean

    createdAt: number

    metadata?: Record<
        string,
        unknown
    >
}

export interface RuntimeApplicationRegistryState {

    initialized: boolean

    applicationsMounted: number
}

export class RuntimeApplicationRegistry {

    public readonly state:
        RuntimeApplicationRegistryState

    private applications:
        Map<
            string,
            RuntimeApplication
        >

    constructor() {

        this.applications =
            new Map()

        this.state = {

            initialized: false,

            applicationsMounted: 0
        }
    }

    /**
     * ---------------------------------------------------
     * Registry Initialization
     * ---------------------------------------------------
     */

    public async initialize():
        Promise<void> {

        console.log(
            "[RuntimeApplicationRegistry] initialize"
        )

        this.state.initialized = true

        console.log(
            "[RuntimeApplicationRegistry] ready"
        )
    }

    /**
     * ---------------------------------------------------
     * Application Registration
     * ---------------------------------------------------
     */

    public register(
        application:
            RuntimeApplication
    ): void {

        if (
            this.applications.has(
                application.id
            )
        ) {

            console.warn(
                `[RuntimeApplicationRegistry] duplicate application: ${application.id}`
            )

            return
        }

        this.applications.set(
            application.id,
            application
        )

        this.state
            .applicationsMounted += 1

        console.log(
            "[RuntimeApplicationRegistry] mounted",
            application.id
        )
    }

    /**
     * ---------------------------------------------------
     * Application Removal
     * ---------------------------------------------------
     */

    public unregister(
        applicationId: string
    ): void {

        if (
            !this.applications.has(
                applicationId
            )
        ) {

            return
        }

        this.applications.delete(
            applicationId
        )

        this.state
            .applicationsMounted -= 1

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

    public get(
        applicationId: string
    ):
        RuntimeApplication | undefined {

        return this.applications.get(
            applicationId
        )
    }

    public getAll():
        RuntimeApplication[] {

        return Array.from(
            this.applications.values()
        )
    }

    public has(
        applicationId: string
    ): boolean {

        return this.applications.has(
            applicationId
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

            applications:
                this.getAll()
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

            applicationsMounted:
                this.state
                    .applicationsMounted,

            registeredApplications:
                this.applications.size
        }
    }
}