import React from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

import {
    RuntimeWindowState
} from "./RuntimeWorkspace"

export interface RuntimeWindowManagerProps {

    runtimeOS: RuntimeOS
}

export const RuntimeWindowManager: React.FC<
    RuntimeWindowManagerProps
> = ({ runtimeOS }) => {

    const windows =
        runtimeOS.workspace.layout.windows

    /**
     * ---------------------------------------------------
     * Window Focus
     * ---------------------------------------------------
     */

    const handleFocus = (
        windowId: string
    ) => {

        runtimeOS.workspace
            .focusWindow(windowId)
    }

    /**
     * ---------------------------------------------------
     * Window Render
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                absolute
                inset-0
                overflow-hidden
            "
        >

            {
                windows.map((window) => (

                    <RuntimeWindow
                        key={window.id}
                        window={window}
                        onFocus={() =>
                            handleFocus(window.id)
                        }
                    />
                ))
            }

        </div>
    )
}

/**
 * ===================================================
 * Runtime Window
 * ===================================================
 */

export interface RuntimeWindowProps {

    window: RuntimeWindowState

    onFocus: () => void
}

export const RuntimeWindow: React.FC<
    RuntimeWindowProps
> = ({
    window,
    onFocus
}) => {

    if (window.minimized) {

        return null
    }

    return (

        <div
            className="
                absolute
                rounded-xl
                overflow-hidden
                border
                border-neutral-800
                bg-neutral-900/90
                backdrop-blur-md
                shadow-2xl
                flex
                flex-col
                select-none
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
            onMouseDown={onFocus}
        >

            {/* -------------------------------- */}
            {/* Window Header */}
            {/* -------------------------------- */}

            <div
                className="
                    h-10
                    border-b
                    border-neutral-800
                    bg-neutral-950
                    flex
                    items-center
                    justify-between
                    px-3
                    shrink-0
                "
            >

                <div
                    className="
                        flex
                        items-center
                        gap-3
                    "
                >

                    {/* ---------------- */}
                    {/* Window Controls */}
                    {/* ---------------- */}

                    <div
                        className="
                            flex
                            items-center
                            gap-2
                        "
                    >

                        <div
                            className="
                                w-3
                                h-3
                                rounded-full
                                bg-red-500
                            "
                        />

                        <div
                            className="
                                w-3
                                h-3
                                rounded-full
                                bg-yellow-500
                            "
                        />

                        <div
                            className="
                                w-3
                                h-3
                                rounded-full
                                bg-green-500
                            "
                        />

                    </div>

                    {/* ---------------- */}
                    {/* Title */}
                    {/* ---------------- */}

                    <div
                        className="
                            text-sm
                            font-semibold
                            tracking-wide
                        "
                    >
                        {window.title}
                    </div>

                </div>

                {/* ---------------- */}
                {/* Runtime Metadata */}
                {/* ---------------- */}

                <div
                    className="
                        text-[10px]
                        font-mono
                        opacity-50
                        flex
                        items-center
                        gap-3
                    "
                >

                    <div>
                        app:
                        {" "}
                        {window.applicationId}
                    </div>

                    <div>
                        z:
                        {" "}
                        {window.zIndex}
                    </div>

                </div>

            </div>

            {/* -------------------------------- */}
            {/* Window Body */}
            {/* -------------------------------- */}

            <div
                className="
                    flex-1
                    relative
                    overflow-hidden
                    bg-neutral-900
                "
            >

                {/* ---------------- */}
                {/* Window Grid */}
                {/* ---------------- */}

                <div
                    className="
                        absolute
                        inset-0
                        opacity-[0.04]
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
                            "24px 24px"
                    }}
                />

                {/* ---------------- */}
                {/* Placeholder */}
                {/* ---------------- */}

                <div
                    className="
                        absolute
                        inset-0
                        flex
                        flex-col
                        items-center
                        justify-center
                        gap-3
                    "
                >

                    <div
                        className="
                            text-xl
                            font-semibold
                        "
                    >
                        {window.title}
                    </div>

                    <div
                        className="
                            text-xs
                            opacity-50
                            font-mono
                        "
                    >
                        application:
                        {" "}
                        {window.applicationId}
                    </div>

                    <div
                        className="
                            text-[10px]
                            opacity-40
                            max-w-sm
                            text-center
                            leading-relaxed
                        "
                    >
                        Graph-native runtime
                        projection surface bound
                        to deterministic replay
                        topology and websocket
                        synchronized execution
                        continuity.
                    </div>

                </div>

            </div>

            {/* -------------------------------- */}
            {/* Window Footer */}
            {/* -------------------------------- */}

            <div
                className="
                    h-6
                    border-t
                    border-neutral-800
                    bg-neutral-950
                    flex
                    items-center
                    justify-between
                    px-3
                    text-[10px]
                    font-mono
                    opacity-50
                    shrink-0
                "
            >

                <div>
                    focused:
                    {" "}
                    {
                        window.focused
                            ? "true"
                            : "false"
                    }
                </div>

                <div>
                    size:
                    {" "}
                    {window.size.width}
                    ×
                    {window.size.height}
                </div>

            </div>

        </div>
    )
}