import React, {
    useMemo
} from "react"

import {
    RuntimeWorkspace
} from "./RuntimeWorkspace"

import {
    RuntimeWindowManager
} from "./RuntimeWindowManager"

import {
    RuntimeApplicationRegistry
} from "./RuntimeApplicationRegistry"

import {
    RuntimeViewport
} from "./RuntimeViewport"

/**
 * HHS Runtime Desktop
 * ---------------------------------------------------
 * Canonical Runtime OS desktop manifold.
 *
 * Responsibilities:
 *
 * - Runtime workspace composition
 * - Window projection
 * - Runtime viewport orchestration
 * - Graph-native desktop topology
 * - Replay-linked workspace continuity
 * - Runtime process projection
 * - Application surface rendering
 * - Runtime overlay composition
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeDesktopProps {

    workspace: RuntimeWorkspace

    windowManager: RuntimeWindowManager

    registry: RuntimeApplicationRegistry
}

export const RuntimeDesktop: React.FC<
    RuntimeDesktopProps
> = ({
    workspace,
    windowManager,
    registry
}) => {

    /**
     * ---------------------------------------------------
     * Runtime Windows
     * ---------------------------------------------------
     */

    const windows =
        useMemo(() => {

            return windowManager
                .getWindows()
                .sort(

                    (a, b) =>
                        a.zIndex - b.zIndex
                )

        }, [windowManager])

    /**
     * ---------------------------------------------------
     * Window Close
     * ---------------------------------------------------
     */

    const closeWindow = (
        windowId: string,
        applicationId: string
    ) => {

        windowManager.destroyWindow(
            windowId
        )

        registry.unmountApplication(
            applicationId
        )
    }

    /**
     * ---------------------------------------------------
     * Window Focus
     * ---------------------------------------------------
     */

    const focusWindow = (
        windowId: string
    ) => {

        windowManager.focusWindow(
            windowId
        )
    }

    /**
     * ---------------------------------------------------
     * Runtime Desktop
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                relative
                w-full
                h-full
                overflow-hidden
                bg-black
            "
        >

            {/* -------------------------------- */}
            {/* Runtime Viewport */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    inset-0
                "
            >

                <RuntimeViewport
                    workspace={workspace}
                />

            </div>

            {/* -------------------------------- */}
            {/* Runtime Window Layer */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    inset-0
                    pointer-events-none
                "
            >

                {
                    windows.map(

                        (runtimeWindow) => {

                            if (
                                runtimeWindow.minimized
                            ) {

                                return null
                            }

                            const application =
                                registry
                                    .getApplication(

                                        runtimeWindow
                                            .applicationId
                                    )

                            return (

                                <div

                                    key={
                                        runtimeWindow.id
                                    }

                                    onMouseDown={() => {

                                        focusWindow(
                                            runtimeWindow.id
                                        )
                                    }}

                                    className={`
                                        absolute
                                        rounded-2xl
                                        overflow-hidden
                                        border
                                        backdrop-blur-xl
                                        pointer-events-auto
                                        transition-all
                                        duration-200

                                        ${
                                            runtimeWindow.focused
                                                ? `
                                                    border-cyan-500
                                                    shadow-[0_0_40px_rgba(34,211,238,0.25)]
                                                  `
                                                : `
                                                    border-neutral-800
                                                  `
                                        }
                                    `}

                                    style={{

                                        left:
                                            runtimeWindow
                                                .position.x,

                                        top:
                                            runtimeWindow
                                                .position.y,

                                        width:
                                            runtimeWindow
                                                .size.width,

                                        height:
                                            runtimeWindow
                                                .size.height,

                                        zIndex:
                                            runtimeWindow
                                                .zIndex
                                    }}
                                >

                                    {/* ---------------- */}
                                    {/* Window Header */}
                                    {/* ---------------- */}

                                    <div
                                        className="
                                            h-12
                                            border-b
                                            border-neutral-800
                                            bg-neutral-950/90
                                            flex
                                            items-center
                                            justify-between
                                            px-4
                                        "
                                    >

                                        <div
                                            className="
                                                flex
                                                flex-col
                                            "
                                        >

                                            <div
                                                className="
                                                    text-sm
                                                    font-medium
                                                "
                                            >
                                                {
                                                    runtimeWindow.title
                                                }
                                            </div>

                                            <div
                                                className="
                                                    text-[10px]
                                                    opacity-50
                                                    font-mono
                                                "
                                            >
                                                {
                                                    application
                                                        ?.applicationType
                                                }
                                            </div>

                                        </div>

                                        {/* ------------ */}
                                        {/* Controls */}
                                        {/* ------------ */}

                                        <div
                                            className="
                                                flex
                                                items-center
                                                gap-2
                                            "
                                        >

                                            <button

                                                onClick={() => {

                                                    windowManager
                                                        .minimizeWindow(

                                                            runtimeWindow.id
                                                        )
                                                }}

                                                className="
                                                    w-3
                                                    h-3
                                                    rounded-full
                                                    bg-yellow-400
                                                "
                                            />

                                            <button

                                                onClick={() => {

                                                    windowManager
                                                        .maximizeWindow(

                                                            runtimeWindow.id
                                                        )
                                                }}

                                                className="
                                                    w-3
                                                    h-3
                                                    rounded-full
                                                    bg-green-400
                                                "
                                            />

                                            <button

                                                onClick={() => {

                                                    closeWindow(

                                                        runtimeWindow.id,

                                                        runtimeWindow.applicationId
                                                    )
                                                }}

                                                className="
                                                    w-3
                                                    h-3
                                                    rounded-full
                                                    bg-red-400
                                                "
                                            />

                                        </div>

                                    </div>

                                    {/* ---------------- */}
                                    {/* Window Content */}
                                    {/* ---------------- */}

                                    <div
                                        className="
                                            w-full
                                            h-[calc(100%-48px)]
                                            bg-neutral-950/90
                                            flex
                                            items-center
                                            justify-center
                                            relative
                                        "
                                    >

                                        {/* ------------ */}
                                        {/* Placeholder */}
                                        {/* ------------ */}

                                        <div
                                            className="
                                                flex
                                                flex-col
                                                items-center
                                                gap-4
                                                text-center
                                            "
                                        >

                                            <div
                                                className="
                                                    text-2xl
                                                    font-semibold
                                                "
                                            >
                                                {
                                                    runtimeWindow.title
                                                }
                                            </div>

                                            <div
                                                className="
                                                    text-xs
                                                    opacity-50
                                                    font-mono
                                                "
                                            >
                                                Runtime application surface
                                            </div>

                                            <div
                                                className="
                                                    text-[10px]
                                                    opacity-30
                                                    max-w-sm
                                                    leading-relaxed
                                                "
                                            >
                                                Graph-native deterministic
                                                runtime application manifold
                                                projected into replay-linked
                                                Runtime OS workspace topology.
                                            </div>

                                        </div>

                                    </div>

                                </div>
                            )
                        }
                    )
                }

            </div>

        </div>
    )
}