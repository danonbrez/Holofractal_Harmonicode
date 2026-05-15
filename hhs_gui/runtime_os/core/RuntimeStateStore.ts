/**
 * =========================================================
 * RuntimeStateStore
 * =========================================================
 *
 * Canonical frontend runtime projection cache.
 *
 * IMPORTANT
 * ---------------------------------------------------------
 * This store is NOT runtime authority.
 *
 * Runtime authority belongs to:
 *
 *   - backend runtime
 *   - replay engine
 *   - receipt lineage
 *   - runtime event schema
 *
 * This layer only:
 *
 *   - caches
 *   - indexes
 *   - projects
 *   - visualizes
 *   - snapshots
 *
 * NEVER derive runtime truth here.
 */

import type {
    RuntimeSocketEvent
} from "./RuntimeSocketManager"

// =========================================================
// Graph Node
// =========================================================

export interface RuntimeGraphNode {

    id: string

    parent?: string

    runtime_id?: string

    branch_id?: string

    receipt_hash72?: string

    event_type?: string

    timestamp_ns?: number

    payload?: Record<
        string,
        unknown
    >
}

// =========================================================
// Timeline Frame
// =========================================================

export interface RuntimeTimelineFrame {

    event_type: string

    sequence_id?: number

    runtime_id?: string

    branch_id?: string

    event_hash72?: string

    parent_event_hash72?: string

    receipt_hash72?: string

    timestamp_ns?: number

    payload?: Record<
        string,
        unknown
    >
}

// =========================================================
// Runtime Snapshot
// =========================================================

export interface RuntimeSnapshot {

    created_at_ns: number

    total_events: number

    graph_nodes: number

    replay_frames: number
}

// =========================================================
// RuntimeStateStore
// =========================================================

export class RuntimeStateStore {

    // =====================================================
    // Runtime Events
    // =====================================================

    private readonly events:
        RuntimeSocketEvent[] = []

    // =====================================================
    // Replay Timeline
    // =====================================================

    private readonly timeline:
        RuntimeTimelineFrame[] = []

    // =====================================================
    // Graph Projection
    // =====================================================

    private readonly graphNodes =
        new Map<
            string,
            RuntimeGraphNode
        >()

    // =====================================================
    // Runtime Index
    // =====================================================

    private readonly runtimeIndex =
        new Map<
            string,
            RuntimeSocketEvent[]
        >()

    // =====================================================
    // Branch Index
    // =====================================================

    private readonly branchIndex =
        new Map<
            string,
            RuntimeSocketEvent[]
        >()

    // =====================================================
    // Receipt Index
    // =====================================================

    private readonly receiptIndex =
        new Map<
            string,
            RuntimeSocketEvent[]
        >()

    // =====================================================
    // Limits
    // =====================================================

    private readonly maxEvents =
        4096

    private readonly maxTimeline =
        4096

    // =====================================================
    // Ingest Event
    // =====================================================

    public ingestEvent(
        event: RuntimeSocketEvent
    ): void {

        // -------------------------------------------------
        // Event Cache
        // -------------------------------------------------

        this.events.push(event)

        if (
            this.events.length
            >
            this.maxEvents
        ) {

            this.events.splice(

                0,

                this.events.length
                -
                this.maxEvents
            )
        }

        // -------------------------------------------------
        // Timeline
        // -------------------------------------------------

        this.timeline.push({

            event_type:
                event.event_type,

            sequence_id:
                event.sequence_id,

            runtime_id:
                event.runtime_id,

            branch_id:
                event.branch_id,

            event_hash72:
                event.event_hash72,

            parent_event_hash72:
                event.parent_event_hash72,

            receipt_hash72:
                event.receipt_hash72,

            timestamp_ns:
                event.timestamp_ns,

            payload:
                event.payload
        })

        if (
            this.timeline.length
            >
            this.maxTimeline
        ) {

            this.timeline.splice(

                0,

                this.timeline.length
                -
                this.maxTimeline
            )
        }

        // -------------------------------------------------
        // Graph Projection
        // -------------------------------------------------

        if (event.event_hash72) {

            this.graphNodes.set(

                event.event_hash72,

                {

                    id:
                        event.event_hash72,

                    parent:
                        event.parent_event_hash72,

                    runtime_id:
                        event.runtime_id,

                    branch_id:
                        event.branch_id,

                    receipt_hash72:
                        event.receipt_hash72,

                    event_type:
                        event.event_type,

                    timestamp_ns:
                        event.timestamp_ns,

                    payload:
                        event.payload
                }
            )
        }

        // -------------------------------------------------
        // Runtime Index
        // -------------------------------------------------

        if (event.runtime_id) {

            if (
                !this.runtimeIndex.has(
                    event.runtime_id
                )
            ) {

                this.runtimeIndex.set(

                    event.runtime_id,

                    []
                )
            }

            this.runtimeIndex
                .get(event.runtime_id)
                ?.push(event)
        }

        // -------------------------------------------------
        // Branch Index
        // -------------------------------------------------

        if (event.branch_id) {

            if (
                !this.branchIndex.has(
                    event.branch_id
                )
            ) {

                this.branchIndex.set(

                    event.branch_id,

                    []
                )
            }

            this.branchIndex
                .get(event.branch_id)
                ?.push(event)
        }

        // -------------------------------------------------
        // Receipt Index
        // -------------------------------------------------

        if (event.receipt_hash72) {

            if (
                !this.receiptIndex.has(
                    event.receipt_hash72
                )
            ) {

                this.receiptIndex.set(

                    event.receipt_hash72,

                    []
                )
            }

            this.receiptIndex
                .get(event.receipt_hash72)
                ?.push(event)
        }
    }

    // =====================================================
    // Timeline
    // =====================================================

    public getTimeline():
        RuntimeTimelineFrame[] {

        return [
            ...this.timeline
        ]
    }

    // =====================================================
    // Graph
    // =====================================================

    public getGraphNodes():
        RuntimeGraphNode[] {

        return [

            ...this.graphNodes
                .values()
        ]
    }

    // =====================================================
    // Events
    // =====================================================

    public getEvents():
        RuntimeSocketEvent[] {

        return [
            ...this.events
        ]
    }

    // =====================================================
    // Runtime Query
    // =====================================================

    public getRuntimeEvents(
        runtime_id: string
    ): RuntimeSocketEvent[] {

        return [

            ...(this.runtimeIndex.get(
                runtime_id
            ) ?? [])
        ]
    }

    // =====================================================
    // Branch Query
    // =====================================================

    public getBranchEvents(
        branch_id: string
    ): RuntimeSocketEvent[] {

        return [

            ...(this.branchIndex.get(
                branch_id
            ) ?? [])
        ]
    }

    // =====================================================
    // Receipt Query
    // =====================================================

    public getReceiptEvents(
        receipt_hash72: string
    ): RuntimeSocketEvent[] {

        return [

            ...(this.receiptIndex.get(
                receipt_hash72
            ) ?? [])
        ]
    }

    // =====================================================
    // Snapshot
    // =====================================================

    public createSnapshot():
        RuntimeSnapshot {

        return {

            created_at_ns:
                Date.now() * 1_000_000,

            total_events:
                this.events.length,

            graph_nodes:
                this.graphNodes.size,

            replay_frames:
                this.timeline.length
        }
    }

    // =====================================================
    // Reset
    // =====================================================

    public reset():
        void {

        this.events.length = 0

        this.timeline.length = 0

        this.graphNodes.clear()

        this.runtimeIndex.clear()

        this.branchIndex.clear()

        this.receiptIndex.clear()
    }

    // =====================================================
    // Metrics
    // =====================================================

    public getMetrics() {

        return {

            events:
                this.events.length,

            timeline:
                this.timeline.length,

            graphNodes:
                this.graphNodes.size,

            runtimes:
                this.runtimeIndex.size,

            branches:
                this.branchIndex.size,

            receipts:
                this.receiptIndex.size
        }
    }
}