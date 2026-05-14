import React from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

export interface RuntimeWindowManagerProps {

    runtimeOS: RuntimeOS
}

export const RuntimeWindowManager: React.FC<
    RuntimeWindowManagerProps
> = ({ runtimeOS }) => {

    const windows =
        runtimeOS.workspace.layout.windows

    return (

        <>

            {
                windows.map((window) => (

                    <div
                        key={window.id}
                        className="
                            absolute
                            border
                            border-neutral-700
                            bg-neutral-900
                            rounded-lg
                            overflow-hidden
                            shadow-2xl
                        "
                        style={{

                            left:
                                window.position.x,

                            top:
                                window.position.y,

                            width:
                                window.size.width,

                            height:
                                window.size.height,

                            zIndex:
                                window.zIndex
                        }}
                    >

                        {/* ---------------- */}
                        {/* Window Header */}
                        {/* ---------------- */}

                        <div
                            className="
                                h-10
                                border-b
                                border-neutral-800
                                flex
                                items-center
                                px-3
                                bg-neutral-950
                                text-sm
                                font-semibold
                            "
                        >
                            {window.title}
                        </div>

                        {/* ---------------- */}
                        {/* Window Body */}
                        {/* ---------------- */}

                        <div
                            className="
                                w-full
                                h-[calc(100%-40px)]
                                bg-neutral-900
                            "
                        />

                    </div>
                ))
            }

        </>
    )
}