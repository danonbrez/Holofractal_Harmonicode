import React, {
    useEffect,
    useMemo,
    useRef,
    useState
} from "react"

import * as THREE from "three"

import {
    Canvas,
    useFrame
} from "@react-three/fiber"

import {
    Grid,
    Html,
    Line,
    OrbitControls
} from "@react-three/drei"

import {
    RuntimeExecutionAuthority
} from "../../runtime_os/core/RuntimeExecutionAuthority"

import {
    RuntimeKernelBridge
} from "../../runtime_os/core/RuntimeKernelBridge"

/**
 * HHS Runtime Breadboard
 * ---------------------------------------------------
 * Runtime-authorized graph projection surface.
 *
 * CRITICAL:
 *
 * GUI nodes are NOT execution nodes.
 *
 * GUI edges are NOT execution edges.
 *
 * This component does NOT:
 *
 * - execute runtime graph logic locally
 * - simulate VM execution locally
 * - resolve transport locally
 * - generate replay locally
 * - generate receipt topology locally
 * - mutate runtime graph state directly
 *
 * ALL AUTHORITATIVE TOPOLOGY
 * ORIGINATES FROM:
 *
 * Runtime
 * → Kernel
 * → Receipts
 * → Replay
 * → Runtime graph updates
 *
 * GUI ONLY PROJECTS
 * RUNTIME-AUTHORIZED STRUCTURE.
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface HHSRuntimeBreadboardProps {

    authority: RuntimeExecutionAuthority

    kernelBridge: RuntimeKernelBridge
}

export interface RuntimeBreadboardNode {

    id: string

    runtimeNodeId: string

    position: [number, number, number]

    nodeType: string

    status: string

    receiptHash?: string
}

export interface RuntimeBreadboardEdge {

    id: string

    source: [number, number, number]

    target: [number, number, number]

    transportType: string
}

const BreadboardNode: React.FC<{

    node: RuntimeBreadboardNode

    selected: boolean

}> = ({
    node,
    selected
}) => {

    const meshRef =
        useRef<THREE.Mesh>(null)

    useFrame((state) => {

        if (!meshRef.current) {

            return
        }

        meshRef.current.rotation.y += 0.01

        const pulse =

            1 +

            Math.sin(
                state.clock.elapsedTime * 3
            ) * 0.06

        meshRef.current.scale.set(

            pulse,
            pulse,
            pulse
        )
    })

    const color =

        selected
            ? "#22d3ee"

        : node.status === "active"
            ? "#4ade80"

        : node.status === "warning"
            ? "#f59e0b"

        : "#c084fc"

    return (

        <group position={node.position}>

            <mesh ref={meshRef}>

                <boxGeometry
                    args={[0.8, 0.8, 0.8]}
                />

                <meshStandardMaterial

                    color={color}

                    emissive={color}

                    emissiveIntensity={0.9}
                />

            </mesh>

            <Html
                distanceFactor={10}
            >

                <div
                    className="
                        min-w-[140px]
                        rounded-xl
                        border
                        border-neutral-700
                        bg-black/80
                        backdrop-blur-xl
                        p-3
                        text-[10px]
                        font-mono
                        text-neutral-200
                    "
                >

                    <div
                        className="
                            text-cyan-300
                            font-semibold
                            mb-2
                        "
                    >
                        runtime node
                    </div>

                    <div>
                        type:
                        {" "}
                        {
                            node.nodeType
                        }
                    </div>

                    <div>
                        status:
                        {" "}
                        {
                            node.status
                        }
                    </div>

                    <div
                        className="
                            opacity-60
                            mt-2
                            break-all
                        "
                    >
                        {
                            node.runtimeNodeId
                        }
                    </div>

                </div>

            </Html>

        </group>
    )
}

export const HHSRuntimeBreadboard:
React.FC<
    HHSRuntimeBreadboardProps
> = ({
    authority,
    kernelBridge
}) => {

    const [nodes, setNodes] =
        useState<
            RuntimeBreadboardNode[]
        >([])

    const [selectedNodeId, setSelectedNodeId] =
        useState<string | null>(null)

    /**
     * ---------------------------------------------------
     * Runtime Graph Subscription
     * ---------------------------------------------------
     */

    useEffect(() => {

        const runtimeGraphHandler = (
            payload: any
        ) => {

            /**
             * IMPORTANT:
             *
             * GUI spatializes runtime-originated
             * graph updates only.
             *
             * Runtime truth remains authoritative.
             */

            const runtimeNodes =
                payload?.nodes ?? []

            const projectedNodes:
                RuntimeBreadboardNode[] =

                runtimeNodes.map(

                    (
                        runtimeNode: any,
                        index: number
                    ) => {

                        const angle =

                            index * 0.45

                        const radius =
                            6 +
                            (index % 5)

                        return {

                            id:
                                crypto.randomUUID(),

                            runtimeNodeId:

                                runtimeNode.id ??

                                `runtime-${index}`,

                            nodeType:

                                runtimeNode.type ??

                                "runtime_operator",

                            status:

                                runtimeNode.status ??

                                "active",

                            receiptHash:

                                runtimeNode.receiptHash,

                            position: [

                                Math.cos(angle) * radius,

                                Math.sin(angle * 2) * 2,

                                Math.sin(angle) * radius
                            ]
                        }
                    }
                )

            setNodes(projectedNodes)
        }

        kernelBridge.on(
            "graph_update",
            runtimeGraphHandler
        )

        return () => {

            kernelBridge.off(
                "graph_update",
                runtimeGraphHandler
            )
        }

    }, [kernelBridge])

    /**
     * ---------------------------------------------------
     * Projection Edges
     * ---------------------------------------------------
     */

    const edges =
        useMemo<
            RuntimeBreadboardEdge[]
        >(() => {

            const projectionEdges:
                RuntimeBreadboardEdge[] = []

            for (
                let i = 0;
                i < nodes.length - 1;
                i++
            ) {

                projectionEdges.push({

                    id:
                        `edge-${i}`,

                    source:
                        nodes[i].position,

                    target:
                        nodes[i + 1].position,

                    transportType:
                        "runtime_transport"
                })
            }

            return projectionEdges

        }, [nodes])

    /**
     * ---------------------------------------------------
     * Runtime Node Activation
     * ---------------------------------------------------
     */

    const activateRuntimeNode = (
        node:
            RuntimeBreadboardNode
    ) => {

        setSelectedNodeId(
            node.id
        )

        /**
         * IMPORTANT:
         *
         * Interaction routes through authority.
         *
         * GUI never mutates runtime directly.
         */

        authority.execute({

            operation:
                "runtime.node.inspect",

            payload: {

                runtimeNodeId:
                    node.runtimeNodeId,

                receiptHash:
                    node.receiptHash
            },

            requiresReceipt: true,

            requiresReplayLink: true,

            sourceComponent:
                "HHSRuntimeBreadboard"
        })
    }

    /**
     * ---------------------------------------------------
     * Selected Node
     * ---------------------------------------------------
     */

    const selectedNode =
        useMemo(() => {

            if (!selectedNodeId) {

                return undefined
            }

            return nodes.find(

                (node) =>
                    node.id === selectedNodeId
            )

        }, [
            nodes,
            selectedNodeId
        ])

    /**
     * ---------------------------------------------------
     * Projection Surface
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                w-full
                h-full
                bg-black
                relative
            "
        >

            {/* -------------------------------- */}
            {/* Runtime Projection Canvas */}
            {/* -------------------------------- */}

            <Canvas

                camera={{

                    position: [0, 10, 18],

                    fov: 60
                }}
            >

                <ambientLight intensity={0.7} />

                <pointLight

                    position={[10, 10, 10]}

                    intensity={1.6}
                />

                <pointLight

                    position={[-10, -5, -10]}

                    intensity={0.7}

                    color="#22d3ee"
                />

                {/* ---------------------------- */}
                {/* Runtime Grid */}
                {/* ---------------------------- */}

                <Grid

                    args={[100, 100]}

                    cellSize={1}

                    sectionSize={5}

                    fadeDistance={50}
                />

                {/* ---------------------------- */}
                {/* Runtime Edges */}
                {/* ---------------------------- */}

                {
                    edges.map((edge) => (

                        <Line

                            key={edge.id}

                            points={[

                                edge.source,

                                edge.target
                            ]}

                            color="#22d3ee"

                            transparent

                            opacity={0.4}

                            lineWidth={1.2}
                        />
                    ))
                }

                {/* ---------------------------- */}
                {/* Runtime Nodes */}
                {/* ---------------------------- */}

                {
                    nodes.map((node) => (

                        <group
                            key={node.id}

                            onClick={() => {

                                activateRuntimeNode(
                                    node
                                )
                            }}
                        >

                            <BreadboardNode

                                node={node}

                                selected={
                                    selectedNodeId ===
                                    node.id
                                }
                            />

                        </group>
                    ))
                }

                {/* ---------------------------- */}
                {/* Controls */}
                {/* ---------------------------- */}

                <OrbitControls

                    enableDamping

                    dampingFactor={0.08}

                    rotateSpeed={0.7}

                    zoomSpeed={0.7}
                />

            </Canvas>

            {/* -------------------------------- */}
            {/* Overlay */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    top-4
                    left-4
                    flex
                    flex-col
                    gap-2
                    text-[10px]
                    font-mono
                "
            >

                <div
                    className="
                        px-3
                        py-2
                        rounded-xl
                        border
                        border-neutral-800
                        bg-black/70
                        backdrop-blur-xl
                    "
                >
                    runtime-authorized topology only
                </div>

                <div
                    className="
                        px-3
                        py-2
                        rounded-xl
                        border
                        border-neutral-800
                        bg-black/70
                        backdrop-blur-xl
                    "
                >
                    projected runtime nodes:
                    {" "}
                    {
                        nodes.length
                    }
                </div>

                <div
                    className="
                        px-3
                        py-2
                        rounded-xl
                        border
                        border-neutral-800
                        bg-black/70
                        backdrop-blur-xl
                    "
                >
                    authority locked:
                    {" "}
                    {
                        authority.state
                            .authorityLocked

                            ? "TRUE"

                            : "FALSE"
                    }
                </div>

            </div>

            {/* -------------------------------- */}
            {/* Runtime Inspector */}
            {/* -------------------------------- */}

            {
                selectedNode && (

                    <div
                        className="
                            absolute
                            bottom-4
                            right-4
                            w-[360px]
                            rounded-2xl
                            border
                            border-neutral-800
                            bg-black/80
                            backdrop-blur-xl
                            overflow-hidden
                        "
                    >

                        <div
                            className="
                                px-4
                                py-3
                                border-b
                                border-neutral-800
                                text-sm
                                font-semibold
                                text-cyan-300
                            "
                        >
                            Runtime Node Inspector
                        </div>

                        <div
                            className="
                                p-4
                                flex
                                flex-col
                                gap-3
                                text-[10px]
                                font-mono
                            "
                        >

                            <div>

                                <div
                                    className="
                                        opacity-50
                                        mb-1
                                    "
                                >
                                    runtimeNodeId
                                </div>

                                <div
                                    className="
                                        break-all
                                    "
                                >
                                    {
                                        selectedNode
                                            .runtimeNodeId
                                    }
                                </div>

                            </div>

                            <div>

                                <div
                                    className="
                                        opacity-50
                                        mb-1
                                    "
                                >
                                    nodeType
                                </div>

                                <div>
                                    {
                                        selectedNode
                                            .nodeType
                                    }
                                </div>

                            </div>

                            <div>

                                <div
                                    className="
                                        opacity-50
                                        mb-1
                                    "
                                >
                                    status
                                </div>

                                <div>
                                    {
                                        selectedNode
                                            .status
                                    }
                                </div>

                            </div>

                            <div>

                                <div
                                    className="
                                        opacity-50
                                        mb-1
                                    "
                                >
                                    receiptHash
                                </div>

                                <div
                                    className="
                                        break-all
                                    "
                                >
                                    {
                                        selectedNode
                                            .receiptHash ??
                                            "runtime-linked"
                                    }
                                </div>

                            </div>

                        </div>

                    </div>
                )
            }

        </div>
    )
}