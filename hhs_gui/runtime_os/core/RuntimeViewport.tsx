import React from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

export interface RuntimeViewportProps {

    runtimeOS: RuntimeOS
}

export const RuntimeViewport: React.FC<
    RuntimeViewportProps
> = ({ runtimeOS }) => {

    const viewport =
        runtimeOS.workspace.layout.viewport

    /**
     * ---------------------------------------------------
     * Projection Mode
     * ---------------------------------------------------
     */

    const projectionMode =
        viewport.projectionMode

    /**
     * ---------------------------------------------------
     * Viewport Render
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                absolute
                inset-0
                overflow-hidden
                bg-neutral-950
            "
        >

            {/* -------------------------------- */}
            {/* Runtime Grid */}
            {/* -------------------------------- */}

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
                        `
                        ${32 * viewport.zoom}px
                        ${32 * viewport.zoom}px
                        `
                }}
            />

            {/* -------------------------------- */}
            {/* Coordinate Axes */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    left-1/2
                    top-0
                    bottom-0
                    w-px
                    bg-cyan-500/10
                "
                style={{

                    transform:
                        `
                        translateX(
                            ${viewport.cameraX}px
                        )
                        `
                }}
            />

            <div
                className="
                    absolute
                    top-1/2
                    left-0
                    right-0
                    h-px
                    bg-cyan-500/10
                "
                style={{

                    transform:
                        `
                        translateY(
                            ${viewport.cameraY}px
                        )
                        `
                }}
            />

            {/* -------------------------------- */}
            {/* Projection Surface */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    inset-0
                    flex
                    items-center
                    justify-center
                "
            >

                <div
                    className="
                        flex
                        flex-col
                        items-center
                        gap-4
                    "
                >

                    <div
                        className="
                            text-4xl
                            font-bold
                            tracking-wide
                        "
                    >
                        Runtime Viewport
                    </div>

                    <div
                        className="
                            text-sm
                            opacity-60
                            font-mono
                        "
                    >
                        projection:
                        {" "}
                        {projectionMode}
                    </div>

                    <div
                        className="
                            text-xs
                            opacity-40
                            font-mono
                        "
                    >
                        camera:
                        {" "}
                        (
                        {viewport.cameraX},
                        {" "}
                        {viewport.cameraY}
                        )
                    </div>

                    <div
                        className="
                            text-xs
                            opacity-40
                            font-mono
                        "
                    >
                        zoom:
                        {" "}
                        {viewport.zoom}
                    </div>

                </div>

            </div>

            {/* -------------------------------- */}
            {/* Viewport HUD */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    top-6
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
                    viewport:
                    {" "}
                    online
                </div>

                <div>
                    projection:
                    {" "}
                    {projectionMode}
                </div>

                <div>
                    graph:
                    {" "}
                    {
                        runtimeOS.state.graphReady
                            ? "online"
                            : "offline"
                    }
                </div>

                <div>
                    replay:
                    {" "}
                    {
                        runtimeOS.state.replayReady
                            ? "online"
                            : "offline"
                    }
                </div>

                <div>
                    transport:
                    {" "}
                    {
                        runtimeOS.state.transportReady
                            ? "online"
                            : "offline"
                    }
                </div>

            </div>

        </div>
    )
}