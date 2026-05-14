import React from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

import {
    RuntimeWindowState
} from "./RuntimeWorkspace"

import {
    RuntimeWindowContent
} from "./RuntimeWindowContent"

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
     * Focus Window
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
     * Close Window
     * ---------------------------------------------------
     */

    const handleClose = (
        windowId: string
    ) => {

        runtimeOS.workspace
            .removeWindow(windowId)
    }

    /**
     * ---------------------------------------------------
     * Minimize Window
     * ---------------------------------------------------
     */

    const handleMinimize = (
        windowId: string
    ) => {

        const target =
            runtimeOS.workspace
                .layout.windows
                .find(
                    (window) =>
                        window.id ===
                        windowId
                )

        if (!target) {

            return
        }

        target.minimized =
            !target.minimized
    }

    /**
     * ---------------------------------------------------
     * Maximize Window
     * ---------------------------------------------------
     */

    const handleMaximize = (
        windowId: string
    ) => {

        const target =
            runtimeOS.workspace
                .layout.windows
                .find(
                    (window) =>
                        window.id ===
                        windowId
                )

        if (!target) {

            return
        }

        target.maximized =
            !target.maximized

        if (target.maximized) {

            target.position = {

                x: 24,

                y: 24
            }

            target.size = {

                width:
                    window.innerWidth - 96,

                height:
                    window.innerHeight - 160
            }
        }
    }

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
            "
        >

            {
                windows.map((window) => (

                    <RuntimeWindow
                        key={window.id}

                        runtimeOS={runtimeOS}

                        window={window}

                        onFocus={() =>
                            handleFocus(
                                window.id
                            )
                        }

                        onClose={() =>
                            handleClose(
                                window.id
                            )
                        }

                        onMinimize={() =>
                            handleMinimize(
                                window.id
                            )
                        }

                        onMaximize={() =>
                            handleMaximize(
                                window.id
                            )
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

    runtimeOS: RuntimeOS

    window: RuntimeWindowState

    onFocus: () => void

    onClose: () => void

    onMinimize: () => void

    onMaximize: () => void
}

export const RuntimeWindow: React.FC<
    RuntimeWindowProps
> = ({
    runtimeOS,
    window,
    onFocus,
    onClose,
    onMinimize,
    onMaximize
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
                    {/* Controls */}
                    {/* ---------------- */}

                    <div
                        className="
                            flex
                            items-center
                            gap-2
                        "
                    >

                        <button
                            onClick={onClose}
                            className="
                                w-3
                                h-3
                                rounded-full
                                bg-red-500
                                hover:scale-110
                                transition
                            "
                        />

                        <button
                            onClick={onMinimize}
                            className="
                                w-3
                                h-3
                                rounded-full
                                bg-yellow-500
                                hover:scale-110
                                transition
                            "
                        />

                        <button
                            onClick={onMaximize}
                            className="
                                w-3
                                h-3
                                rounded-full
                                bg-green-500
                                hover:scale-110
                                transition
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
                {/* Metadata */}
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

                <RuntimeWindowContent
                    runtimeOS={runtimeOS}
                    applicationId={
                        window.applicationId
                    }
                />

            </div>

            {/* -------------------------------- */}
            {/* Footer */}
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