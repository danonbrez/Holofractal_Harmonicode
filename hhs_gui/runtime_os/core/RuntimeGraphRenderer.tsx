import React, {
    useMemo
} from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

export interface RuntimeGraphNode {

    id: string

    label: string

    type: string

    x: number

    y: number

    z?: number
}

export interface RuntimeGraphEdge {

    id: string

    source: string

    target: string

    transportType?: string
}

export interface RuntimeGraphRendererProps {

    runtimeOS: RuntimeOS

    nodes: RuntimeGraphNode[]

    edges: RuntimeGraphEdge[]
}

export const RuntimeGraphRenderer: React.FC<
    RuntimeGraphRendererProps
> = ({
    runtimeOS,
    nodes,
    edges
}) => {

    /**
     * ---------------------------------------------------
     * Node Lookup
     * ---------------------------------------------------
     */

    const nodeMap = useMemo(() => {

        const map =
            new Map<
                string,
                RuntimeGraphNode
            >()

        for (
            const node
            of nodes
        ) {

            map.set(
                node.id,
                node
            )
        }

        return map

    }, [nodes])

    /**
     * ---------------------------------------------------
     * Render
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                absolute
                inset-0
                overflow-hidden
                pointer-events-none
            "
        >

            {/* -------------------------------- */}
            {/* SVG Edge Layer */}
            {/* -------------------------------- */}

            <svg
                className="
                    absolute
                    inset-0
                    w-full
                    h-full
                "
            >

                <defs>

                    <linearGradient
                        id="runtimeEdgeGradient"
                        x1="0%"
                        y1="0%"
                        x2="100%"
                        y2="0%"
                    >

                        <stop
                            offset="0%"
                            stopColor="
                                rgba(
                                    34,
                                    211,
                                    238,
                                    0.15
                                )
                            "
                        />

                        <stop
                            offset="100%"
                            stopColor="
                                rgba(
                                    168,
                                    85,
                                    247,
                                    0.15
                                )
                            "
                        />

                    </linearGradient>

                </defs>

                {
                    edges.map((edge) => {

                        const source =
                            nodeMap.get(
                                edge.source
                            )

                        const target =
                            nodeMap.get(
                                edge.target
                            )

                        if (
                            !source ||
                            !target
                        ) {

                            return null
                        }

                        return (

                            <g
                                key={edge.id}
                            >

                                {/* ------------ */}
                                {/* Glow */}
                                {/* ------------ */}

                                <line
                                    x1={source.x}
                                    y1={source.y}
                                    x2={target.x}
                                    y2={target.y}
                                    stroke="
                                        rgba(
                                            34,
                                            211,
                                            238,
                                            0.08
                                        )
                                    "
                                    strokeWidth="10"
                                />

                                {/* ------------ */}
                                {/* Core */}
                                {/* ------------ */}

                                <line
                                    x1={source.x}
                                    y1={source.y}
                                    x2={target.x}
                                    y2={target.y}
                                    stroke="
                                        url(
                                            #runtimeEdgeGradient
                                        )
                                    "
                                    strokeWidth="2"
                                />

                            </g>
                        )
                    })
                }

            </svg>

            {/* -------------------------------- */}
            {/* Graph Nodes */}
            {/* -------------------------------- */}

            {
                nodes.map((node) => (

                    <div
                        key={node.id}
                        className="
                            absolute
                            rounded-2xl
                            border
                            border-cyan-500/20
                            bg-neutral-900/80
                            backdrop-blur-md
                            shadow-2xl
                            px-4
                            py-3
                            min-w-[160px]
                            flex
                            flex-col
                            gap-2
                        "
                        style={{

                            left:
                                node.x,

                            top:
                                node.y,

                            transform:
                                `
                                translate(
                                    -50%,
                                    -50%
                                )
                                `
                        }}
                    >

                        {/* ---------------- */}
                        {/* Node Header */}
                        {/* ---------------- */}

                        <div
                            className="
                                flex
                                items-center
                                justify-between
                                gap-4
                            "
                        >

                            <div
                                className="
                                    text-sm
                                    font-semibold
                                "
                            >
                                {node.label}
                            </div>

                            <div
                                className="
                                    w-2
                                    h-2
                                    rounded-full
                                    bg-cyan-400
                                "
                            />

                        </div>

                        {/* ---------------- */}
                        {/* Metadata */}
                        {/* ---------------- */}

                        <div
                            className="
                                text-[10px]
                                font-mono
                                opacity-50
                            "
                        >
                            type:
                            {" "}
                            {node.type}
                        </div>

                        <div
                            className="
                                text-[10px]
                                font-mono
                                opacity-40
                                break-all
                            "
                        >
                            id:
                            {" "}
                            {node.id}
                        </div>

                    </div>
                ))
            }

            {/* -------------------------------- */}
            {/* Runtime Graph HUD */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    bottom-6
                    left-6
                    rounded-xl
                    border
                    border-neutral-800
                    bg-neutral-900/80
                    backdrop-blur-md
                    px-4
                    py-3
                    text-xs
                    font-mono
                    flex
                    flex-col
                    gap-2
                    shadow-2xl
                "
            >

                <div>
                    graph:
                    {" "}
                    active
                </div>

                <div>
                    nodes:
                    {" "}
                    {nodes.length}
                </div>

                <div>
                    edges:
                    {" "}
                    {edges.length}
                </div>

                <div>
                    replay:
                    {" "}
                    {
                        runtimeOS.state
                            .replayReady
                                ? "online"
                                : "offline"
                    }
                </div>

                <div>
                    transport:
                    {" "}
                    {
                        runtimeOS.state
                            .transportReady
                                ? "online"
                                : "offline"
                    }
                </div>

            </div>

        </div>
    )
}