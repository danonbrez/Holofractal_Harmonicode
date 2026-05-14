import React from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

export interface RuntimeSidebarProps {

    runtimeOS: RuntimeOS
}

export const RuntimeSidebar: React.FC<
    RuntimeSidebarProps
> = ({ runtimeOS }) => {

    const metrics =
        runtimeOS.getMetrics()

    const applicationsMounted =
        metrics.applicationsMounted as number

    return (

        <div
            className="
                absolute
                top-12
                left-0
                bottom-0
                w-72
                border-r
                border-neutral-800
                bg-neutral-900/80
                backdrop-blur-xl
                z-[1200]
                flex
                flex-col
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
                    flex
                    items-center
                    px-4
                    text-sm
                    font-semibold
                "
            >
                Runtime Navigation
            </div>

            {/* -------------------------------- */}
            {/* Navigation */}
            {/* -------------------------------- */}

            <div
                className="
                    flex-1
                    overflow-auto
                    p-3
                    flex
                    flex-col
                    gap-2
                "
            >

                {
                    [
                        "Runtime Console",

                        "Calculator",

                        "Breadboard",

                        "Graph Debugger",

                        "Tensor Inspector",

                        "Replay Viewer"
                    ].map((item) => (

                        <button
                            key={item}
                            className="
                                runtime-button
                                w-full
                                text-left
                                px-3
                                py-2
                                text-sm
                            "
                        >
                            {item}
                        </button>
                    ))
                }

            </div>

            {/* -------------------------------- */}
            {/* Footer */}
            {/* -------------------------------- */}

            <div
                className="
                    border-t
                    border-neutral-800
                    p-4
                    text-xs
                    font-mono
                    opacity-50
                    flex
                    flex-col
                    gap-2
                "
            >

                <div>
                    apps:
                    {" "}
                    {applicationsMounted}
                </div>

                <div>
                    workspace:
                    {" "}
                    {
                        runtimeOS.workspace.id
                    }
                </div>

            </div>

        </div>
    )
}