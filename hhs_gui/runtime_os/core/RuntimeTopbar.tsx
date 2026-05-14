import React from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

export interface RuntimeTopbarProps {

    runtimeOS: RuntimeOS
}

export const RuntimeTopbar: React.FC<
    RuntimeTopbarProps
> = ({ runtimeOS }) => {

    const metrics =
        runtimeOS.getMetrics()

    const uptime =
        Math.floor(
            metrics.uptimeMs as number
        )

    return (

        <div
            className="
                absolute
                top-0
                left-0
                right-0
                h-10
                z-[1500]
                border-b
                border-neutral-800
                bg-neutral-950/80
                backdrop-blur-xl
                flex
                items-center
                justify-between
                px-4
                text-xs
                font-mono
            "
        >

            <div
                className="
                    flex
                    items-center
                    gap-4
                "
            >

                <div
                    className="
                        font-semibold
                        tracking-wide
                        text-cyan-400
                    "
                >
                    HHS
                </div>

                <div
                    className="
                        opacity-50
                    "
                >
                    Runtime OS
                </div>

            </div>

            <div
                className="
                    flex
                    items-center
                    gap-4
                "
            >

                <div>
                    uptime:
                    {" "}
                    {uptime}
                    ms
                </div>

                <div>
                    windows:
                    {" "}
                    {
                        runtimeOS.workspace
                            .layout.windows.length
                    }
                </div>

            </div>

        </div>
    )
}