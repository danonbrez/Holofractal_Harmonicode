/**
 * =========================================================
 * RuntimeStateStore
 * =========================================================
 *
 * Canonical Runtime OS frontend state authority.
 *
 * Responsibilities:
 *
 * - runtime timeline
 * - receipt lineage
 * - graph topology
 * - transport state
 * - replay continuity
 * - websocket event ingestion
 * - runtime observers
 */

import type {
    RuntimeSocketEvent
} from "../core/RuntimeSocketManager"

// =========================================================
// Timeline
// =========================================================

export interface RuntimeTimelineFrame {

    sequence_id: number

    timestamp_ns: number

    event_type: string

    payload: Record<
        string,
        unknown
    >
}

// =========================================================
// Receipts
// =========================================================

export interface RuntimeReceipt {

    receipt_hash72: string

    source_hash72: string

    operation: string

    closure_class: string

    converged: boolean

    halted: boolean
}

// =========================================================
// Graph
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
// Runtime State
// =========================================================

export interface RuntimeState {

    timeline:
        RuntimeTimelineFrame[]

    receipts:
        RuntimeReceipt[]

    graphNodes:
        RuntimeGraphNode[]

    graphEdges:
        RuntimeGraphEdge[]

    transportState:
        Record<
            string,
            unknown
        >

    lastRuntimeEvent?:
        RuntimeSocketEvent

    lastReplayEvent?:
        RuntimeSocketEvent

    lastGraphEvent?:
        RuntimeSocketEvent

    lastTransportEvent?:
        RuntimeSocketEvent
}

// =========================================================
// Observer
// =========================================================

export type RuntimeStateObserver =
    (
        state: RuntimeState
    ) => void

// =========================================================
// Constants
// =========================================================

const MAX_TIMELINE_FRAMES = 4096

const MAX_RECEIPTS = 4096

// =========================================================
// RuntimeStateStore
// =========================================================

export class RuntimeStateStore {

    private readonly state:
        RuntimeState

    private readonly observers =
        new Set<
            RuntimeStateObserver
        >()

    // =====================================================
    // Constructor
    // =====================================================

    constructor() {

        this.state = {

            timeline: [],

            receipts: [],

            graphNodes: [],

            graphEdges: [],

            transportState: {}
        }
    }

    // =====================================================
    // Subscribe
    // =====================================================

    public subscribe(
        observer:
            RuntimeStateObserver
    ): () => void {

        this.observers.add(
            observer
        )

        observer(
            this.snapshot()
        )

        return () => {

            this.observers.delete(
                observer
            )
        }
    }

    // =====================================================
    // Notify
    // =====================================================

    private notify():
        void {

        const snapshot =
            this.snapshot()

        for (
            const observer
            of this.observers
        ) {

            observer(snapshot)
        }
    }

    // =====================================================
    // Snapshot
    // =====================================================

    public snapshot():
        RuntimeState {

        return {

            timeline: [

                ...this.state.timeline
            ],

            receipts: [

                ...this.state.receipts
            ],

            graphNodes: [

                ...this.state.graphNodes
            ],

            graphEdges: [

                ...this.state.graphEdges
            ],

            transportState: {

                ...this.state
                    .transportState
            },

            lastRuntimeEvent:

                this.state
                    .lastRuntimeEvent,

            lastReplayEvent:

                this.state
                    .lastReplayEvent,

            lastGraphEvent:

                this.state
                    .lastGraphEvent,

            lastTransportEvent:

                this.state
                    .lastTransportEvent
        }
    }

    // =====================================================
    // Event Ingestion
    // =====================================================

    public ingestEvent(
        event:
            RuntimeSocketEvent
    ): void {

        // -------------------------------------------------
        // Timeline
        // -------------------------------------------------

        this.state.timeline.push({

            sequence_id:

                event.sequence_id
                ?? 0,

            timestamp_ns:

                event.timestamp_ns
                ?? Date.now(),

            event_type:

                event.event_type
                ?? "runtime",

            payload:

                event.payload
                ?? {}
        })

        // -------------------------------------------------
        // Trim Timeline
        // -------------------------------------------------

        if (

            this.state.timeline.length

            > MAX_TIMELINE_FRAMES

        ) {

            this.state.timeline.shift()
        }

        // -------------------------------------------------
        // Routing
        // -------------------------------------------------

        switch (
            event.event_type
        ) {

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

        this.notify()
    }

    // =====================================================
    // Runtime
    // =====================================================

    private ingestRuntime(
        event:
            RuntimeSocketEvent
    ): void {

        this.state.lastRuntimeEvent =
            event
    }

    // =====================================================
    // Replay
    // =====================================================

    private ingestReplay(
        event:
            RuntimeSocketEvent
    ): void {

        this.state.lastReplayEvent =
            event
    }

    // =====================================================
    // Graph
    // =====================================================

    private ingestGraph(
        event:
            RuntimeSocketEvent
    ): void {

        this.state.lastGraphEvent =
            event

        const payload =
            event.payload
            ?? {}

        const nodes = (
            payload.nodes
            ?? []
        ) as RuntimeGraphNode[]

        const edges = (
            payload.edges
            ?? []
        ) as RuntimeGraphEdge[]

        this.state.graphNodes =
            nodes

        this.state.graphEdges =
            edges
    }

    // =====================================================
    // Transport
    // =====================================================

    private ingestTransport(
        event:
            RuntimeSocketEvent
    ): void {

        this.state.lastTransportEvent =
            event

        this.state.transportState = {

            ...event.payload
        }
    }

    // =====================================================
    // Receipt
    // =====================================================

    private ingestReceipt(
        event:
            RuntimeSocketEvent
    ): void {

        const payload =
            event.payload
            ?? {}

        const receipt:
            RuntimeReceipt = {

            receipt_hash72:

                String(
                    payload
                        .receipt_hash72
                        ?? ""
                ),

            source_hash72:

                String(
                    payload
                        .source_hash72
                        ?? ""
                ),

            operation:

                String(
                    payload
                        .operation
                        ?? "runtime"
                ),

            closure_class:

                String(
                    payload
                        .closure_class
                        ?? "stable"
                ),

            converged:

                Boolean(
                    payload
                        .converged
                ),

            halted:

                Boolean(
                    payload
                        .halted
                )
        }

        this.state.receipts.unshift(
            receipt
        )

        // -------------------------------------------------
        // Trim
        // -------------------------------------------------

        if (

            this.state.receipts.length

            > MAX_RECEIPTS

        ) {

            this.state.receipts.pop()
        }
    }

    // =====================================================
    // Timeline
    // =====================================================

    public getTimeline():
        RuntimeTimelineFrame[] {

        return [

            ...this.state.timeline
        ]
    }

    // =====================================================
    // Receipts
    // =====================================================

    public getReceipts():
        RuntimeReceipt[] {

        return [

            ...this.state.receipts
        ]
    }

    // =====================================================
    // Graph
    // =====================================================

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

    public getMetrics() {

        return {

            timelineFrames:

                this.state.timeline
                    .length,

            receipts:

                this.state.receipts
                    .length,

            graphNodes:

                this.state.graphNodes
                    .length,

            graphEdges:

                this.state.graphEdges
                    .length,

            observers:

                this.observers.size
        }
    }
}