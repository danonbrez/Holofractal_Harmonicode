/**
 * =========================================================
 * RuntimeGraphProjectionEngine
 * =========================================================
 *
 * Converts runtime timeline + receipt lineage into:
 *
 * - graph topology
 * - transport edges
 * - constraint manifolds
 * - replay geometry
 * - execution continuity maps
 *
 * This replaces synthetic fallback topology with:
 *
 * runtime-derived graph structure.
 */

import type {

    RuntimeTimelineFrame,

    RuntimeGraphNode,

    RuntimeGraphEdge,

    RuntimeReceipt

} from "../state/RuntimeStateStore"

// =========================================================
// Types
// =========================================================

export interface RuntimeGraphProjection {

    nodes: RuntimeGraphNode[]

    edges: RuntimeGraphEdge[]
}

// ---------------------------------------------------------

export interface RuntimeProjectionMetrics {

    runtimeNodes: number

    receiptNodes: number

    transportEdges: number

    replayEdges: number

    constraintEdges: number
}

// =========================================================
// Engine
// =========================================================

export class RuntimeGraphProjectionEngine {

    // =====================================================
    // Projection
    // =====================================================

    public buildProjection(

        timeline:
            RuntimeTimelineFrame[],

        receipts:
            RuntimeReceipt[]

    ): RuntimeGraphProjection {

        const nodes:
            RuntimeGraphNode[] = []

        const edges:
            RuntimeGraphEdge[] = []

        // =================================================
        // Timeline Nodes
        // =================================================

        timeline.forEach(

            (
                frame,
                index
            ) => {

                const theta =

                    (
                        index
                        / Math.max(
                            timeline.length,
                            1
                        )
                    )

                    *

                    Math.PI

                    *

                    2

                const radius =

                    4

                    +

                    (
                        index
                        * 0.12
                    )

                nodes.push({

                    node_id:

                        `timeline_${index}`,

                    node_type:

                        frame.event_type,

                    x:

                        Math.cos(theta)
                        * radius,

                    y:

                        Math.sin(theta)
                        * radius,

                    z:

                        index
                        * 0.08,

                    authority:
                        "timeline"
                })

                // -----------------------------------------
                // Sequential Replay Edge
                // -----------------------------------------

                if (
                    index > 0
                ) {

                    edges.push({

                        source:

                            `timeline_${index - 1}`,

                        target:

                            `timeline_${index}`,

                        edge_type:
                            "replay"
                    })
                }
            }
        )

        // =================================================
        // Receipt Nodes
        // =================================================

        receipts.forEach(

            (
                receipt,
                index
            ) => {

                const theta =

                    (
                        index
                        / Math.max(
                            receipts.length,
                            1
                        )
                    )

                    *

                    Math.PI

                    *

                    4

                const radius =

                    8

                    +

                    (
                        index
                        * 0.08
                    )

                nodes.push({

                    node_id:

                        `receipt_${index}`,

                    node_type:
                        "receipt",

                    x:

                        Math.cos(theta)
                        * radius,

                    y:

                        Math.sin(theta)
                        * radius,

                    z:

                        (
                            index
                            * 0.04
                        )

                        +

                        2,

                    authority:
                        "receipt"
                })

                // -----------------------------------------
                // Receipt Continuity
                // -----------------------------------------

                if (
                    index > 0
                ) {

                    edges.push({

                        source:

                            `receipt_${index - 1}`,

                        target:

                            `receipt_${index}`,

                        edge_type:
                            "transport"
                    })
                }
            }
        )

        // =================================================
        // Timeline → Receipt Binding
        // =================================================

        const pairCount = Math.min(

            timeline.length,

            receipts.length
        )

        for (
            let i = 0;
            i < pairCount;
            i++
        ) {

            edges.push({

                source:
                    `timeline_${i}`,

                target:
                    `receipt_${i}`,

                edge_type:
                    "constraint"
            })
        }

        // =================================================
        // Cross-Manifold Constraints
        // =================================================

        for (
            let i = 0;
            i < receipts.length;
            i += 3
        ) {

            if (
                i + 3
                < receipts.length
            ) {

                edges.push({

                    source:
                        `receipt_${i}`,

                    target:
                        `receipt_${i + 3}`,

                    edge_type:
                        "constraint"
                })
            }
        }

        return {

            nodes,

            edges
        }
    }

    // =====================================================
    // Metrics
    // =====================================================

    public metrics(
        projection:
            RuntimeGraphProjection
    ):
        RuntimeProjectionMetrics {

        let transportEdges = 0

        let replayEdges = 0

        let constraintEdges = 0

        for (
            const edge
            of projection.edges
        ) {

            switch (
                edge.edge_type
            ) {

                case "transport":

                    transportEdges += 1

                    break

                case "replay":

                    replayEdges += 1

                    break

                case "constraint":

                    constraintEdges += 1

                    break
            }
        }

        return {

            runtimeNodes:

                projection.nodes.filter(

                    (
                        node
                    ) => (

                        node.authority
                        === "timeline"
                    )
                ).length,

            receiptNodes:

                projection.nodes.filter(

                    (
                        node
                    ) => (

                        node.authority
                        === "receipt"
                    )
                ).length,

            transportEdges,

            replayEdges,

            constraintEdges
        }
    }

    // =====================================================
    // Diffusion
    // =====================================================

    public diffuseProjection(

        projection:
            RuntimeGraphProjection,

        delta: number

    ): RuntimeGraphProjection {

        return {

            nodes:

                projection.nodes.map(

                    (
                        node,
                        index
                    ) => {

                        const phase =

                            delta

                            +

                            (
                                index
                                * 0.12
                            )

                        return {

                            ...node,

                            x:

                                node.x

                                +

                                Math.sin(
                                    phase
                                )

                                *

                                0.03,

                            y:

                                node.y

                                +

                                Math.cos(
                                    phase
                                )

                                *

                                0.03
                        }
                    }
                ),

            edges:
                projection.edges
        }
    }
}

// =========================================================
// Global Projection Engine
// =========================================================

export const runtimeGraphProjectionEngine =
    new RuntimeGraphProjectionEngine()