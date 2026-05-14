import React from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

import {
    RuntimeViewport
} from "./RuntimeViewport"

import {
    RuntimeWindowManager
} from "./RuntimeWindowManager"

export interface RuntimeDesktopProps {

    runtimeOS: RuntimeOS
}

export const RuntimeDesktop: React.FC<
    RuntimeDesktopProps
> = ({ runtimeOS }) => {

    /**
     * ---------------------------------------------------
     * Desktop Metrics
     * ---------------------------------------------------
     */

    const metrics =
        runtimeOS.getMetrics()

    /**
     * ---------------------------------------------------
     * Desktop Render
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
            {/* Runtime Viewport */}
            {/* -------------------------------- */}

            <RuntimeViewport
                runtimeOS={runtimeOS}
            />

            {/* -------------------------------- */}
            {/* Window Topology */}
            {/* -------------------------------- */}

            <RuntimeWindowManager
                runtimeOS={runtimeOS}
            />

            {/* -------------------------------- */}
            {/* Desktop Overlay */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    inset-0
                    pointer-events-none
                "
            >

                {/* ---------------- */}
                {/* Gradient Overlay */}
                {/* ---------------- */}

                <div
                    className="
                        absolute
                        inset-0
                        bg-gradient-to-b
                        from-cyan-500/[0.02]
                        via-transparent
                        to-transparent
                    "
                />

                {/* ---------------- */}
                {/* Radial Field */}
                {/* ---------------- */}

                <div
                    className="
                        absolute
                        inset-0
                    "
                    style={{

                        background:
                            `
                            radial-gradient(
                                circle at center,
                                rgba(
                                    34,
                                    211,
                                    238,
                                    0.06
                                ) 0%,
                                transparent 70%
                            )
                            `
                    }}
                />

            </div>

            {/* -------------------------------- */}
            {/* Runtime Desktop HUD */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    top-6
                    left-6
                    z-[1000]
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
                    desktop:
                    {" "}
                    active
                </div>

                <div>
                    windows:
                    {" "}
                    {
                        runtimeOS.workspace
                            .layout.windows.length
                    }
                </div>

                <div>
                    apps:
                    {" "}
                    {
                        runtimeOS.state
                            .applicationsMounted
                    }
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
                    graph:
                    {" "}
                    {
                        runtimeOS.state
                            .graphReady
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

                <div>
                    uptime:
                    {" "}
                    {
                        Math.floor(
                            metrics
                                .uptimeMs
                                    as number
                        )
                    }
                    ms
                </div>

            </div>

        </div>
    )
}