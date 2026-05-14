import React, {
    useMemo,
    useState
} from "react"

export interface RuntimeBreadboardNode {

    id: string

    label: string

    type: string

    x: number

    y: number
}

export interface RuntimeBreadboardEdge {

    id: string

    source: string

    target: string
}

export const RuntimeBreadboard: React.FC =
    () => {

    /**
     * ---------------------------------------------------
     * Runtime Nodes
     * ---------------------------------------------------
     */

    const [
        nodes,
        setNodes
    ] = useState<
        RuntimeBreadboardNode[]
    >([

        {
            id: "runtime",

            label: "Runtime",

            type: "kernel",

            x: 220,

            y: 160
        },

        {
            id: "graph",

            label: "Graph",

            type: "graph",

            x: 520,

            y: 240
        },

        {
            id: "transport",

            label: "Transport",

            type: "transport",

            x: 420,

            y: 420
        },

        {
            id: "replay",

            label: "Replay",

            type: "replay",

            x: 760,

            y: 320
        }
    ])

    /**
     * ---------------------------------------------------
     * Runtime Edges
     * ---------------------------------------------------
     */

    const [
        edges
    ] = useState<
        RuntimeBreadboardEdge[]
    >([

        {
            id: "e1",

            source: "runtime",

            target: "graph"
        },

        {
            id: "e2",

            source: "graph",

            target: "transport"
        },

        {
            id: "e3",

            source: "graph",

            target: "replay"
        }
    ])

    /**
     * ---------------------------------------------------
     * Graph Lookup
     * ---------------------------------------------------
     */

    const nodeMap = useMemo(() => {

        const map =
            new Map<
                string,
                RuntimeBreadboardNode
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
     * Node Creation
     * ---------------------------------------------------
     */

    const createNode = () => {

        const id =
            crypto.randomUUID()

        setNodes((prev) => [

            ...prev,

            {

                id,

                label:
                    "Tensor Node",

                type:
                    "tensor",

                x:
                    240 +
                    Math.random() * 400,

                y:
                    160 +
                    Math.random() * 300
            }
        ])
    }

    /**
     * ---------------------------------------------------
     * Render
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                w-full
                h-full
                bg-neutral-950
                text-neutral-100
                flex
                flex-col
                overflow-hidden
            "
        >

            {/* -------------------------------- */}
            {/* Header */}
            {/* -------------------------------- */}

            <div
                className="
                    h-12
                    border-b
                    border-neutral-800
                    px-4
                    flex
                    items-center
                    justify-between
                    shrink-0
                    bg-neutral-900
                "
            >

                <div
                    className="
                        font-semibold
                        tracking-wide
                    "
                >
                    Runtime Breadboard
                </div>

                <div
                    className="
                        flex
                        items-center
                        gap-3
                    "
                >

                    <button
                        onClick={createNode}
                        className="
                            px-3
                            py-1.5
                            rounded-lg
                            bg-cyan-600
                            hover:bg-cyan-500
                            transition
                            text-xs
                            font-semibold
                        "
                    >
                        Add Node
                    </button>

                    <div
                        className="
                            text-xs
                            opacity-50
                            font-mono
                        "
                    >
                        graph-native transport
                    </div>

                </div>

            </div>

            {/* -------------------------------- */}
            {/* Board Surface */}
            {/* -------------------------------- */}

            <div
                className="
                    relative
                    flex-1
                    overflow-hidden
                "
            >

                {/* ---------------- */}
                {/* Grid */}
                {/* ---------------- */}

                <div
                    className="
                        absolute
                        inset-0
                        opacity-[0.05]
                    "
                    style={{

                        backgroundImage:
                            `
                            linear-gradient(
                                rgba(255,255,255,0.08) 1px,
                                transparent 1px
                            ),
                            linear-gradient(
                                90deg,
                                rgba(255,255,255,0.08) 1px,
                                transparent 1px
                            )
                            `,

                        backgroundSize:
                            "32px 32px"
                    }}
                />

                {/* ---------------- */}
                {/* SVG Edge Layer */}
                {/* ---------------- */}

                <svg
                    className="
                        absolute
                        inset-0
                        w-full
                        h-full
                    "
                >

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

                                <line
                                    key={edge.id}
                                    x1={source.x}
                                    y1={source.y}
                                    x2={target.x}
                                    y2={target.y}
                                    stroke="
                                        rgba(
                                            34,
                                            211,
                                            238,
                                            0.6
                                        )
                                    "
                                    strokeWidth="2"
                                />
                            )
                        })
                    }

                </svg>

                {/* ---------------- */}
                {/* Nodes */}
                {/* ---------------- */}

                {
                    nodes.map((node) => (

                        <div
                            key={node.id}
                            className="
                                absolute
                                rounded-xl
                                border
                                border-cyan-500/30
                                bg-neutral-900/90
                                backdrop-blur-md
                                shadow-2xl
                                px-4
                                py-3
                                min-w-[140px]
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
                                    text-[10px]
                                    font-mono
                                    opacity-50
                                "
                            >
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
                                {node.id}
                            </div>

                        </div>
                    ))
                }

                {/* ---------------- */}
                {/* HUD */}
                {/* ---------------- */}

                <div
                    className="
                        absolute
                        bottom-6
                        right-6
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
                        topology:
                        {" "}
                        active
                    </div>

                    <div>
                        transport:
                        {" "}
                        synchronized
                    </div>

                </div>

            </div>

        </div>
    )
}