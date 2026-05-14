import React, {
    useEffect,
    useMemo,
    useRef,
    useState
} from "react"

import {
    Canvas
} from "@react-three/fiber"

import {
    OrbitControls,

    Grid,

    Line,

    Html

} from "@react-three/drei"

import * as THREE from "three"

import {
    RuntimeOS
} from "./RuntimeOS"

import type {

    RuntimeGraphNode,

    RuntimeGraphEdge

} from "../state/RuntimeStateStore"

// =========================================================
// Props
// =========================================================

export interface RuntimeViewportProps {

    runtimeOS: RuntimeOS
}

// =========================================================
// RuntimeViewport
// =========================================================

export const RuntimeViewport: React.FC<
    RuntimeViewportProps
> = ({
    runtimeOS
}) => {

    const [nodes, setNodes] =
        useState<
            RuntimeGraphNode[]
        >([])

    const [edges, setEdges] =
        useState<
            RuntimeGraphEdge[]
        >([])

    const [metrics, setMetrics] =
        useState(

            runtimeOS
                .store
                .getMetrics()
        )

    // =====================================================
    // Runtime Store Subscription
    // =====================================================

    useEffect(() => {

        const unsubscribe =
            runtimeOS.store.subscribe(

                (state) => {

                    setNodes([
                        ...state.graphNodes
                    ])

                    setEdges([
                        ...state.graphEdges
                    ])

                    setMetrics(

                        runtimeOS
                            .store
                            .getMetrics()
                    )
                }
            )

        return () => {

            unsubscribe()
        }

    }, [runtimeOS])

    // =====================================================
    // Default Projection
    // =====================================================

    const projectedNodes =
        useMemo(() => {

            if (
                nodes.length > 0
            ) {

                return nodes
            }

            /**
             * -------------------------------------------------
             * Fallback Lo Shu Projection
             * -------------------------------------------------
             */

            return [

                {
                    node_id: "1",
                    node_type: "runtime",
                    x: -2,
                    y: -2,
                    z: 0
                },

                {
                    node_id: "2",
                    node_type: "runtime",
                    x: 0,
                    y: -2,
                    z: 0
                },

                {
                    node_id: "3",
                    node_type: "runtime",
                    x: 2,
                    y: -2,
                    z: 0
                },

                {
                    node_id: "4",
                    node_type: "runtime",
                    x: -2,
                    y: 0,
                    z: 0
                },

                {
                    node_id: "5",
                    node_type: "runtime",
                    x: 0,
                    y: 0,
                    z: 0
                },

                {
                    node_id: "6",
                    node_type: "runtime",
                    x: 2,
                    y: 0,
                    z: 0
                },

                {
                    node_id: "7",
                    node_type: "runtime",
                    x: -2,
                    y: 2,
                    z: 0
                },

                {
                    node_id: "8",
                    node_type: "runtime",
                    x: 0,
                    y: 2,
                    z: 0
                },

                {
                    node_id: "9",
                    node_type: "runtime",
                    x: 2,
                    y: 2,
                    z: 0
                }
            ]

        }, [nodes])

    // =====================================================
    // Edge Projection
    // =====================================================

    const projectedEdges =
        useMemo(() => {

            if (
                edges.length > 0
            ) {

                return edges
            }

            return [

                {
                    source: "1",
                    target: "5",
                    edge_type: "transport"
                },

                {
                    source: "5",
                    target: "9",
                    edge_type: "transport"
                },

                {
                    source: "3",
                    target: "5",
                    edge_type: "constraint"
                },

                {
                    source: "5",
                    target: "7",
                    edge_type: "constraint"
                }
            ]

        }, [edges])

    // =====================================================
    // Render
    // =====================================================

    return (

        <div
            className="
                absolute
                inset-0
                overflow-hidden
                bg-neutral-950
            "
        >

            <Canvas
                camera={{

                    position: [

                        0,

                        0,

                        12
                    ],

                    fov: 60
                }}
            >

                {/* ============================================= */}
                {/* Scene */}
                {/* ============================================= */}

                <color
                    attach="background"
                    args={["#05070b"]}
                />

                <fog
                    attach="fog"
                    args={[

                        "#05070b",

                        12,

                        32
                    ]}
                />

                {/* ============================================= */}
                {/* Lighting */}
                {/* ============================================= */}

                <ambientLight
                    intensity={0.5}
                />

                <directionalLight
                    position={[

                        4,

                        6,

                        8
                    ]}
                    intensity={1.2}
                />

                {/* ============================================= */}
                {/* Grid */}
                {/* ============================================= */}

                <Grid

                    args={[

                        40,

                        40
                    ]}

                    cellSize={1}

                    cellThickness={0.5}

                    sectionSize={4}

                    sectionThickness={1}

                    fadeDistance={36}

                    fadeStrength={1}

                    infiniteGrid
                />

                {/* ============================================= */}
                {/* Graph Edges */}
                {/* ============================================= */}

                {
                    projectedEdges.map(

                        (
                            edge,
                            index
                        ) => {

                            const source =
                                projectedNodes.find(

                                    (
                                        node
                                    ) => (

                                        node.node_id
                                        === edge.source
                                    )
                                )

                            const target =
                                projectedNodes.find(

                                    (
                                        node
                                    ) => (

                                        node.node_id
                                        === edge.target
                                    )
                                )

                            if (
                                !source
                                ||
                                !target
                            ) {

                                return null
                            }

                            return (

                                <GraphEdgeLine
                                    key={index}
                                    source={source}
                                    target={target}
                                    edgeType={
                                        edge.edge_type
                                    }
                                />
                            )
                        }
                    )
                }

                {/* ============================================= */}
                {/* Graph Nodes */}
                {/* ============================================= */}

                {
                    projectedNodes.map(

                        (
                            node
                        ) => (

                            <GraphNodeMesh
                                key={
                                    node.node_id
                                }
                                node={node}
                            />
                        )
                    )
                }

                {/* ============================================= */}
                {/* Controls */}
                {/* ============================================= */}

                <OrbitControls

                    enablePan

                    enableZoom

                    enableRotate

                    dampingFactor={0.08}
                />

            </Canvas>

            {/* ================================================= */}
            {/* Overlay Metrics */}
            {/* ================================================= */}

            <div
                className="
                    absolute
                    bottom-4
                    left-4
                    z-[2000]
                    rounded-2xl
                    border
                    border-neutral-800
                    bg-neutral-900/80
                    backdrop-blur-xl
                    p-4
                    shadow-2xl
                    text-xs
                    font-mono
                    text-white
                    flex
                    flex-col
                    gap-2
                    min-w-[220px]
                "
            >

                <div
                    className="
                        text-cyan-400
                        font-semibold
                    "
                >
                    Runtime Projection
                </div>

                <ViewportMetric
                    label="nodes"
                    value={
                        String(
                            projectedNodes
                                .length
                        )
                    }
                />

                <ViewportMetric
                    label="edges"
                    value={
                        String(
                            projectedEdges
                                .length
                        )
                    }
                />

                <ViewportMetric
                    label="timeline"
                    value={
                        String(
                            metrics
                                .timelineFrames
                        )
                    }
                />

                <ViewportMetric
                    label="receipts"
                    value={
                        String(
                            metrics
                                .receipts
                        )
                    }
                />

            </div>

        </div>
    )
}

// =========================================================
// Graph Node
// =========================================================

interface GraphNodeMeshProps {

    node: RuntimeGraphNode
}

const GraphNodeMesh: React.FC<
    GraphNodeMeshProps
> = ({
    node
}) => {

    const meshRef =
        useRef<
            THREE.Mesh
        >(null)

    // =====================================================
    // Render
    // =====================================================

    return (

        <group
            position={[

                node.x,

                node.y,

                node.z
            ]}
        >

            <mesh
                ref={meshRef}
            >

                <sphereGeometry
                    args={[

                        0.35,

                        32,

                        32
                    ]}
                />

                <meshStandardMaterial

                    color="#22d3ee"

                    emissive="#22d3ee"

                    emissiveIntensity={0.35}
                />

            </mesh>

            <Html
                center
                distanceFactor={10}
            >

                <div
                    className="
                        px-2
                        py-1
                        rounded-md
                        border
                        border-cyan-500/20
                        bg-black/80
                        backdrop-blur-md
                        text-[10px]
                        font-mono
                        text-cyan-300
                        whitespace-nowrap
                        select-none
                    "
                >
                    {node.node_id}
                </div>

            </Html>

        </group>
    )
}

// =========================================================
// Graph Edge
// =========================================================

interface GraphEdgeLineProps {

    source: RuntimeGraphNode

    target: RuntimeGraphNode

    edgeType: string
}

const GraphEdgeLine: React.FC<
    GraphEdgeLineProps
> = ({
    source,
    target,
    edgeType
}) => {

    const color =

        edgeType === "constraint"
            ? "#f472b6"
            : edgeType === "transport"
                ? "#22d3ee"
                : "#a3a3a3"

    return (

        <Line

            points={[

                [

                    source.x,

                    source.y,

                    source.z
                ],

                [

                    target.x,

                    target.y,

                    target.z
                ]
            ]}

            color={color}

            lineWidth={1}
        />
    )
}

// =========================================================
// Metrics
// =========================================================

interface ViewportMetricProps {

    label: string

    value: string
}

const ViewportMetric: React.FC<
    ViewportMetricProps
> = ({
    label,
    value
}) => {

    return (

        <div
            className="
                flex
                items-center
                justify-between
                gap-6
            "
        >

            <div
                className="
                    opacity-50
                "
            >
                {label}
            </div>

            <div>
                {value}
            </div>

        </div>
    )
}