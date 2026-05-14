/**
 * =========================================================
 * RuntimeStateStore
 * =========================================================
 *
 * Frontend projection-only runtime state authority.
 *
 * IMPORTANT:
 * ---------------------------------------------------------
 * This store is observational only.
 *
 * No execution authority exists here.
 *
 * Backend runtime remains canonical.
 *
 * Responsibilities:
 *
 * - Runtime event ingestion
 * - Replay state projection
 * - Graph projection state
 * - Transport metrics
 * - Receipt lineage
 * - Runtime HUD synchronization
 * - Timeline buffering
 * - Window/application projection state
 */

import type {

    RuntimeSocketEvent,

    RuntimeEventType

} from "../core/RuntimeSocketManager"

// =========================================================
// Graph Types
// =========================================================

export interface RuntimeGraphNode {

    node_id: string

    node_type: string

    x: number

    y: number

    z: number

    authority?: string
}

// ---------------------------------------------------------

export interface RuntimeGraphEdge {

    source: string

    target: string

    edge_type: string
}

// =========================================================
// Receipt Types
// =========================================================

export interface RuntimeReceipt {

    receipt_hash72: string

    source_hash72: string

    operation: string

    closure_class?: string

    converged?: boolean

    halted?: boolean
}

// =========================================================
// Timeline Types
// =========================================================

export interface RuntimeTimelineFrame {

    sequence_id: number

    timestamp_ns: number

    event_type: RuntimeEventType

    payload: Record<
        string,
        unknown
    >
}

// =========================================================
// Runtime Store State
// =========================================================

export interface RuntimeProjectionState {

    runtimeStatus: string

    runtimePhase: string

    runtimeStep: number

    replayStatus: string

    replayTick: number

    transportFlux: number

    throughput: number

    graphNodes:
        RuntimeGraphNode[]

    graphEdges:
        RuntimeGraphEdge[]

    receipts:
        RuntimeReceipt[]

    timeline:
        RuntimeTimelineFrame[]

    lastRuntimeEvent?:
        RuntimeSocketEvent

    lastReplayEvent?:
        RuntimeSocketEvent

    lastGraphEvent?:
        RuntimeSocketEvent

    lastTransportEvent?:
        RuntimeSocketEvent

    totalEvents: number
}

// =========================================================
// Store Listener
// =========================================================

export type RuntimeStoreListener = (

    state: RuntimeProjectionState

) => void

// =========================================================
// RuntimeStateStore
// =========================================================

export class RuntimeStateStore {

    public readonly state:
        RuntimeProjectionState

    private listeners:
        Set<
            RuntimeStoreListener
        >

    private readonly maxTimeline =
        4096

    private readonly maxReceipts =
        2048

    // =====================================================
    // Constructor
    // =====================================================

    constructor() {

        this.listeners =
            new Set()

        this.state = {

            runtimeStatus:
                "booting",

            runtimePhase:
                "bootstrap",

            runtimeStep:
                0,

            replayStatus:
                "offline",

            replayTick:
                0,

            transportFlux:
                0,

            throughput:
                0,

            graphNodes: [],

            graphEdges: [],

            receipts: [],

            timeline: [],

            totalEvents: 0
        }
    }

    // =====================================================
    // Ingest
    // =====================================================

    public ingestEvent(
        event: RuntimeSocketEvent
    ): void {

        this.state.totalEvents += 1

        this.appendTimeline(event)

        switch (event.event_type) {

            case "runtime":

                this.ingestRuntime(
                    event
                )

                break

            case "replay":

                this.ingestReplay(
                    event
                )

                break

            case "graph":

                this.ingestGraph(
                    event
                )

                break

            case "transport":

                this.ingestTransport(
                    event
                )

                break

            case "receipt":

                this.ingestReceipt(
                    event
                )

                break
        }

        this.emit()
    }

    // =====================================================
    // Runtime
    // =====================================================

    private ingestRuntime(
        event: RuntimeSocketEvent
    ): void {

        this.state.lastRuntimeEvent =
            event

        const payload =
            event.payload

        this.state.runtimeStatus =

            String(

                payload.runtime_status
                ?? "online"
            )

        this.state.runtimePhase =

            String(

                payload.phase
                ?? "runtime_loop"
            )

        this.state.runtimeStep =

            Number(

                payload.step
                ?? 0
            )

        if (

            payload.receipt_hash72
            &&
            payload.source_hash72

        ) {

            this.state.receipts.push({

                receipt_hash72:

                    String(
                        payload.receipt_hash72
                    ),

                source_hash72:

                    String(
                        payload.source_hash72
                    ),

                operation:

                    String(
                        payload.operation
                        ?? "runtime"
                    ),

                closure_class:

                    String(
                        payload.closure_state
                        ?? "stable"
                    )
            })

            if (

                this.state.receipts
                    .length

                > this.maxReceipts
            ) {

                this.state.receipts
                    .splice(

                        0,

                        this.state
                            .receipts
                            .length

                        - this.maxReceipts
                    )
            }
        }
    }

    // =====================================================
    // Replay
    // =====================================================

    private ingestReplay(
        event: RuntimeSocketEvent
    ): void {

        this.state.lastReplayEvent =
            event

        const payload =
            event.payload

        this.state.replayStatus =

            String(

                payload.replay_status
                ?? "stable"
            )

        this.state.replayTick =

            Number(

                payload.replay_tick
                ?? 0
            )
    }

    // =====================================================
    // Graph
    // =====================================================

    private ingestGraph(
        event: RuntimeSocketEvent
    ): void {

        this.state.lastGraphEvent =
            event

        const payload =
            event.payload

        const rawNodes =
            payload.nodes

        const rawEdges =
            payload.edges

        if (
            Array.isArray(
                rawNodes
            )
        ) {

            this.state.graphNodes =

                rawNodes.map(

                    (
                        node
                    ) => (

                        node
                        as RuntimeGraphNode
                    )
                )
        }

        if (
            Array.isArray(
                rawEdges
            )
        ) {

            this.state.graphEdges =

                rawEdges.map(

                    (
                        edge
                    ) => (

                        edge
                        as RuntimeGraphEdge
                    )
                )
        }
    }

    // =====================================================
    // Transport
    // =====================================================

    private ingestTransport(
        event: RuntimeSocketEvent
    ): void {

        this.state
            .lastTransportEvent =
                event

        const payload =
            event.payload

        this.state.transportFlux =

            Number(

                payload.transport_flux
                ?? 0
            )

        this.state.throughput =

            Number(

                payload.throughput
                ?? 0
            )
    }

    // =====================================================
    // Receipt
    // =====================================================

    private ingestReceipt(
        event: RuntimeSocketEvent
    ): void {

        const payload =
            event.payload

        const receipt: RuntimeReceipt = {

            receipt_hash72:

                String(
                    payload.receipt_hash72
                    ?? ""
                ),

            source_hash72:

                String(
                    payload.source_hash72
                    ?? ""
                ),

            operation:

                String(
                    payload.operation
                    ?? "unknown"
                ),

            closure_class:

                String(
                    payload.closure_class
                    ?? "stable"
                ),

            converged:

                Boolean(
                    payload.converged
                ),

            halted:

                Boolean(
                    payload.halted
                )
        }

        this.state.receipts.push(
            receipt
        )

        if (

            this.state.receipts
                .length

            > this.maxReceipts
        ) {

            this.state.receipts.splice(

                0,

                this.state
                    .receipts
                    .length

                - this.maxReceipts
            )
        }
    }

    // =====================================================
    // Timeline
    // =====================================================

    private appendTimeline(
        event: RuntimeSocketEvent
    ): void {

        this.state.timeline.push({

            sequence_id:

                Number(
                    event.sequence_id
                    ?? 0
                ),

            timestamp_ns:
                event.timestamp_ns,

            event_type:
                event.event_type,

            payload:
                event.payload
        })

        if (

            this.state.timeline
                .length

            > this.maxTimeline
        ) {

            this.state.timeline
                .splice(

                    0,

                    this.state
                        .timeline
                        .length

                    - this.maxTimeline
                )
        }
    }

    // =====================================================
    // Subscribe
    // =====================================================

    public subscribe(
        listener:
            RuntimeStoreListener
    ): () => void {

        this.listeners.add(
            listener
        )

        return () => {

            this.listeners.delete(
                listener
            )
        }
    }

    // =====================================================
    // Emit
    // =====================================================

    private emit():
        void {

        for (
            const listener
            of this.listeners
        ) {

            try {

                listener(
                    this.state
                )

            } catch (error) {

                console.error(

                    "[RuntimeStateStore] listener failure",

                    error
                )
            }
        }
    }

    // =====================================================
    // Accessors
    // =====================================================

    public getReceipts():
        RuntimeReceipt[] {

        return [
            ...this.state.receipts
        ]
    }

    // -----------------------------------------------------

    public getTimeline():
        RuntimeTimelineFrame[] {

        return [
            ...this.state.timeline
        ]
    }

    // -----------------------------------------------------

    public getGraphNodes():
        RuntimeGraphNode[] {

        return [
            ...this.state.graphNodes
        ]
    }

    // -----------------------------------------------------

    public getGraphEdges():
        RuntimeGraphEdge[] {

        return [
            ...this.state.graphEdges
        ]
    }

    // =====================================================
    // Metrics
    // =====================================================

    public getMetrics():
        object {

        return {

            runtimeStatus:
                this.state
                    .runtimeStatus,

            runtimePhase:
                this.state
                    .runtimePhase,

            runtimeStep:
                this.state
                    .runtimeStep,

            replayStatus:
                this.state
                    .replayStatus,

            replayTick:
                this.state
                    .replayTick,

            transportFlux:
                this.state
                    .transportFlux,

            throughput:
                this.state
                    .throughput,

            receipts:
                this.state
                    .receipts
                    .length,

            graphNodes:
                this.state
                    .graphNodes
                    .length,

            graphEdges:
                this.state
                    .graphEdges
                    .length,

            timelineFrames:
                this.state
                    .timeline
                    .length,

            totalEvents:
                this.state
                    .totalEvents
        }
    }

    // =====================================================
    // Reset
    // =====================================================

    public reset():
        void {

        this.state.runtimeStatus =
            "booting"

        this.state.runtimePhase =
            "bootstrap"

        this.state.runtimeStep =
            0

        this.state.replayStatus =
            "offline"

        this.state.replayTick =
            0

        this.state.transportFlux =
            0

        this.state.throughput =
            0

        this.state.graphNodes =
            []

        this.state.graphEdges =
            []

        this.state.receipts =
            []

        this.state.timeline =
            []

        this.state.totalEvents =
            0

        this.emit()
    }
}