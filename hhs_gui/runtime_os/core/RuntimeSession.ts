/**
 * HHS Runtime Session
 * ---------------------------------------------------
 * Canonical Runtime OS replay-linked session layer.
 *
 * Responsibilities:
 *
 * - Runtime session continuity
 * - Replay-linked session persistence
 * - Workspace restoration
 * - Runtime state snapshots
 * - Session replay reconstruction
 * - Deterministic restoration
 * - Runtime checkpoint orchestration
 * - Transport-linked session continuity
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeSessionSnapshot {

    id: string

    timestamp: number

    workspaceState: object

    routerState: object

    graphState?: object

    replayState?: object

    transportState?: object

    tensorState?: object

    receiptHash?: string
}

export interface RuntimeSessionState {

    initialized: boolean

    restored: boolean

    replayLinked: boolean

    activeSnapshot?: string

    snapshotCount: number

    sessionStart: number
}

export class RuntimeSession {

    public readonly id: string

    public readonly state: RuntimeSessionState

    private readonly snapshots:
        RuntimeSessionSnapshot[]

    private sessionStorageKey: string

    constructor() {

        this.id = crypto.randomUUID()

        this.snapshots = []

        this.sessionStorageKey =
            "HHS_RUNTIME_SESSION"

        this.state = {

            initialized: false,

            restored: false,

            replayLinked: false,

            snapshotCount: 0,

            sessionStart: Date.now()
        }
    }

    /**
     * ---------------------------------------------------
     * Session Initialization
     * ---------------------------------------------------
     */

    public async initialize(): Promise<void> {

        console.log(
            "[RuntimeSession] initialize"
        )

        await this.restorePreviousSession()

        this.state.initialized = true

        this.state.replayLinked = true

        console.log(
            "[RuntimeSession] ready"
        )
    }

    /**
     * ---------------------------------------------------
     * Session Restoration
     * ---------------------------------------------------
     */

    private async restorePreviousSession():
        Promise<void> {

        try {

            const serialized =
                localStorage.getItem(
                    this.sessionStorageKey
                )

            if (!serialized) {

                console.log(
                    "[RuntimeSession] no previous session"
                )

                return
            }

            const parsed =
                JSON.parse(serialized)

            if (
                Array.isArray(parsed.snapshots)
            ) {

                for (
                    const snapshot
                    of parsed.snapshots
                ) {

                    this.snapshots.push(snapshot)
                }
            }

            this.state.restored = true

            this.state.snapshotCount =
                this.snapshots.length

            console.log(
                "[RuntimeSession] restored",
                this.snapshots.length,
                "snapshots"
            )
        }
        catch (error) {

            console.error(
                "[RuntimeSession] restore failure",
                error
            )
        }
    }

    /**
     * ---------------------------------------------------
     * Snapshot Creation
     * ---------------------------------------------------
     */

    public createSnapshot(
        payload: {

            workspaceState: object

            routerState: object

            graphState?: object

            replayState?: object

            transportState?: object

            tensorState?: object

            receiptHash?: string
        }
    ): RuntimeSessionSnapshot {

        const snapshot:
            RuntimeSessionSnapshot = {

            id: crypto.randomUUID(),

            timestamp: Date.now(),

            workspaceState:
                payload.workspaceState,

            routerState:
                payload.routerState,

            graphState:
                payload.graphState,

            replayState:
                payload.replayState,

            transportState:
                payload.transportState,

            tensorState:
                payload.tensorState,

            receiptHash:
                payload.receiptHash
        }

        this.snapshots.push(snapshot)

        this.state.snapshotCount =
            this.snapshots.length

        this.state.activeSnapshot =
            snapshot.id

        console.log(
            "[RuntimeSession] snapshot created",
            snapshot.id
        )

        return snapshot
    }

    /**
     * ---------------------------------------------------
     * Snapshot Persistence
     * ---------------------------------------------------
     */

    public persist(): void {

        try {

            const serialized =
                JSON.stringify({

                    id: this.id,

                    snapshots:
                        this.snapshots,

                    state: this.state
                })

            localStorage.setItem(

                this.sessionStorageKey,

                serialized
            )

            console.log(
                "[RuntimeSession] persisted"
            )
        }
        catch (error) {

            console.error(
                "[RuntimeSession] persist failure",
                error
            )
        }
    }

    /**
     * ---------------------------------------------------
     * Snapshot Retrieval
     * ---------------------------------------------------
     */

    public getSnapshot(
        snapshotId: string
    ): RuntimeSessionSnapshot | undefined {

        return this.snapshots.find(

            (snapshot) =>
                snapshot.id === snapshotId
        )
    }

    public getLatestSnapshot():
        RuntimeSessionSnapshot | undefined {

        if (
            this.snapshots.length === 0
        ) {

            return undefined
        }

        return this.snapshots[
            this.snapshots.length - 1
        ]
    }

    public getSnapshots():
        RuntimeSessionSnapshot[] {

        return this.snapshots
    }

    /**
     * ---------------------------------------------------
     * Snapshot Replay
     * ---------------------------------------------------
     */

    public replaySnapshot(
        snapshotId: string
    ): RuntimeSessionSnapshot | undefined {

        const snapshot =
            this.getSnapshot(snapshotId)

        if (!snapshot) {

            console.warn(
                "[RuntimeSession] snapshot not found",
                snapshotId
            )

            return undefined
        }

        this.state.activeSnapshot =
            snapshot.id

        console.log(
            "[RuntimeSession] replay snapshot",
            snapshot.id
        )

        /**
         * Future:
         *
         * - workspace reconstruction
         * - graph restoration
         * - replay continuity rebuild
         * - transport synchronization
         * - tensor reconstruction
         */

        return snapshot
    }

    /**
     * ---------------------------------------------------
     * Session Reset
     * ---------------------------------------------------
     */

    public clear(): void {

        this.snapshots.length = 0

        this.state.snapshotCount = 0

        this.state.activeSnapshot =
            undefined

        localStorage.removeItem(
            this.sessionStorageKey
        )

        console.log(
            "[RuntimeSession] cleared"
        )
    }

    /**
     * ---------------------------------------------------
     * Session Metrics
     * ---------------------------------------------------
     */

    public getMetrics(): object {

        return {

            initialized:
                this.state.initialized,

            restored:
                this.state.restored,

            replayLinked:
                this.state.replayLinked,

            snapshotCount:
                this.state.snapshotCount,

            uptimeMs:
                Date.now() -
                this.state.sessionStart
        }
    }

    /**
     * ---------------------------------------------------
     * Serialization
     * ---------------------------------------------------
     */

    public serialize(): object {

        return {

            id: this.id,

            state: this.state,

            snapshots:
                this.snapshots
        }
    }
}