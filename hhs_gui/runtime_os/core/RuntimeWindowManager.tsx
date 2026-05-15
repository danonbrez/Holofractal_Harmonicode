import React, {
    useEffect,
    useRef,
    useState
} from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

import {
    RuntimeWindowContent
} from "./RuntimeWindowContent"

// =========================================================
// Props
// =========================================================

export interface RuntimeWindowManagerProps {

    runtimeOS: RuntimeOS

    runtimeWindow: {

        id: string

        title: string

        applicationId: string

        x: number

        y: number

        width: number

        height: number

        minimized: boolean

        maximized: boolean

        focused: boolean
    }

    desktopWidth: number

    desktopHeight: number

    zIndex: number

    onFocus: () => void
}

// =========================================================
// RuntimeWindowManager
// =========================================================

export const RuntimeWindowManager:
React.FC<
    RuntimeWindowManagerProps
> = ({

    runtimeOS,

    runtimeWindow,

    desktopWidth,

    desktopHeight,

    zIndex,

    onFocus
}) => {

    const windowRef =
        useRef<HTMLDivElement>(
            null
        )

    const dragState =
        useRef({

            dragging: false,

            offsetX: 0,

            offsetY: 0
        })

    const resizeState =
        useRef({

            resizing: false,

            startWidth: 0,

            startHeight: 0,

            startMouseX: 0,

            startMouseY: 0
        })

    const [, forceRender] =
        useState(0)

    // =====================================================
    // Sync Render
    // =====================================================

    const sync = () => {

        forceRender(
            (previous) => (

                previous + 1
            )
        )
    }

    // =====================================================
    // Drag Start
    // =====================================================

    const beginDrag = (
        event:
            React.MouseEvent
    ) => {

        onFocus()

        dragState.current.dragging =
            True()

        dragState.current.offsetX = (

            event.clientX
            - runtimeWindow.x
        )

        dragState.current.offsetY = (

            event.clientY
            - runtimeWindow.y
        )

        window.addEventListener(
            "mousemove",
            onDrag
        )

        window.addEventListener(
            "mouseup",
            endDrag
        )
    }

    // =====================================================
    // Drag Move
    // =====================================================

    const onDrag = (
        event: MouseEvent
    ) => {

        if (
            !dragState.current
                .dragging
        ) {

            return
        }

        const nextX = (

            event.clientX

            -

            dragState.current
                .offsetX
        )

        const nextY = (

            event.clientY

            -

            dragState.current
                .offsetY
        )

        runtimeWindow.x = Math.max(

            0,

            Math.min(

                nextX,

                desktopWidth
                - runtimeWindow.width
            )
        )

        runtimeWindow.y = Math.max(

            0,

            Math.min(

                nextY,

                desktopHeight
                - runtimeWindow.height
            )
        )

        sync()
    }

    // =====================================================
    // Drag End
    // =====================================================

    const endDrag = () => {

        dragState.current.dragging =
            false

        window.removeEventListener(
            "mousemove",
            onDrag
        )

        window.removeEventListener(
            "mouseup",
            endDrag
        )
    }

    // =====================================================
    // Resize Begin
    // =====================================================

    const beginResize = (
        event:
            React.MouseEvent
    ) => {

        event.stopPropagation()

        resizeState.current.resizing =
            true

        resizeState.current.startWidth =
            runtimeWindow.width

        resizeState.current.startHeight =
            runtimeWindow.height

        resizeState.current.startMouseX =
            event.clientX

        resizeState.current.startMouseY =
            event.clientY

        window.addEventListener(
            "mousemove",
            onResize
        )

        window.addEventListener(
            "mouseup",
            endResize
        )
    }

    // =====================================================
    // Resize Move
    // =====================================================

    const onResize = (
        event: MouseEvent
    ) => {

        if (
            !resizeState.current
                .resizing
        ) {

            return
        }

        const deltaX = (

            event.clientX

            -

            resizeState.current
                .startMouseX
        )

        const deltaY = (

            event.clientY

            -

            resizeState.current
                .startMouseY
        )

        runtimeWindow.width = Math.max(

            320,

            resizeState.current
                .startWidth

            +

            deltaX
        )

        runtimeWindow.height = Math.max(

            220,

            resizeState.current
                .startHeight

            +

            deltaY
        )

        sync()
    }

    // =====================================================
    // Resize End
    // =====================================================

    const endResize = () => {

        resizeState.current.resizing =
            false

        window.removeEventListener(
            "mousemove",
            onResize
        )

        window.removeEventListener(
            "mouseup",
            endResize
        )
    }

    // =====================================================
    // Cleanup
    // =====================================================

    useEffect(() => {

        return () => {

            endDrag()

            endResize()
        }

    }, [])

    // =====================================================
    // Maximize
    // =====================================================

    const maximize = () => {

        runtimeOS.maximizeWindow(
            runtimeWindow.id
        )

        if (
            runtimeWindow.maximized
        ) {

            runtimeWindow.x = 24

            runtimeWindow.y = 64

            runtimeWindow.width = 920

            runtimeWindow.height = 620

        } else {

            runtimeWindow.x = 0

            runtimeWindow.y = 44

            runtimeWindow.width =
                desktopWidth

            runtimeWindow.height =
                desktopHeight - 44
        }

        sync()
    }

    // =====================================================
    // Minimize
    // =====================================================

    const minimize = () => {

        runtimeOS.minimizeWindow(
            runtimeWindow.id
        )

        sync()
    }

    // =====================================================
    // Render
    // =====================================================

    return (

        <div
            ref={windowRef}
            onMouseDown={onFocus}
            className={`
                absolute
                overflow-hidden
                rounded-2xl
                border
                backdrop-blur-xl
                shadow-2xl
                transition-[box-shadow,border-color]
                duration-150
                ${
                    runtimeWindow.focused

                        ? `
                            border-cyan-500/40
                            shadow-cyan-500/10
                          `

                        : `
                            border-neutral-800
                          `
                }
            `}
            style={{

                left:
                    runtimeWindow.x,

                top:
                    runtimeWindow.y,

                width:
                    runtimeWindow.width,

                height:
                    runtimeWindow.height,

                zIndex
            }}
        >

            {/* ============================================= */}
            {/* Background */}
            {/* ============================================= */}

            <div
                className="
                    absolute
                    inset-0
                    bg-neutral-950/95
                "
            />

            {/* ============================================= */}
            {/* Header */}
            {/* ============================================= */}

            <div
                onMouseDown={beginDrag}
                className="
                    relative
                    h-11
                    shrink-0
                    border-b
                    border-neutral-800
                    bg-neutral-900/90
                    flex
                    items-center
                    justify-between
                    px-4
                    cursor-move
                    select-none
                    z-10
                "
            >

                {/* ----------------------------------------- */}
                {/* Title */}
                {/* ----------------------------------------- */}

                <div
                    className="
                        flex
                        items-center
                        gap-3
                    "
                >

                    <div
                        className={`
                            w-2
                            h-2
                            rounded-full
                            ${
                                runtimeWindow.focused

                                    ? "bg-cyan-400"

                                    : "bg-neutral-600"
                            }
                        `}
                    />

                    <div
                        className="
                            text-sm
                            font-semibold
                            text-white
                            tracking-wide
                        "
                    >
                        {
                            runtimeWindow.title
                        }
                    </div>

                </div>

                {/* ----------------------------------------- */}
                {/* Controls */}
                {/* ----------------------------------------- */}

                <div
                    className="
                        flex
                        items-center
                        gap-2
                    "
                >

                    <button
                        onClick={minimize}
                        className="
                            w-7
                            h-7
                            rounded-lg
                            border
                            border-neutral-700
                            bg-neutral-900
                            text-neutral-400
                            hover:text-white
                            hover:border-neutral-500
                            transition
                            text-xs
                        "
                    >
                        —
                    </button>

                    <button
                        onClick={maximize}
                        className="
                            w-7
                            h-7
                            rounded-lg
                            border
                            border-neutral-700
                            bg-neutral-900
                            text-neutral-400
                            hover:text-white
                            hover:border-neutral-500
                            transition
                            text-xs
                        "
                    >
                        □
                    </button>

                </div>

            </div>

            {/* ============================================= */}
            {/* Content */}
            {/* ============================================= */}

            <div
                className="
                    absolute
                    inset-x-0
                    top-11
                    bottom-0
                    overflow-hidden
                "
            >

                <RuntimeWindowContent
                    runtimeOS={runtimeOS}
                    applicationId={
                        runtimeWindow
                            .applicationId
                    }
                />

            </div>

            {/* ============================================= */}
            {/* Resize Handle */}
            {/* ============================================= */}

            <div
                onMouseDown={beginResize}
                className="
                    absolute
                    bottom-0
                    right-0
                    w-5
                    h-5
                    cursor-se-resize
                    z-20
                "
            >

                <div
                    className="
                        absolute
                        bottom-1
                        right-1
                        w-3
                        h-3
                        border-r
                        border-b
                        border-cyan-500/40
                    "
                />

            </div>

        </div>
    )
}

// =========================================================
// Helpers
// =========================================================

function True(): boolean {

    return true
}