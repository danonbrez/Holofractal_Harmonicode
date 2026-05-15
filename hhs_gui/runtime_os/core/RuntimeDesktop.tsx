import React, {
    useEffect,
    useMemo,
    useState
} from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

import {
    RuntimeWindow
} from "./RuntimeWindowManager"

import {
    RuntimeWindowContent
} from "./RuntimeWindowContent"

// =========================================================
// Props
// =========================================================

export interface RuntimeDesktopProps {

    runtimeOS: RuntimeOS
}

// =========================================================
// RuntimeDesktop
// =========================================================

export const RuntimeDesktop: React.FC<
    RuntimeDesktopProps
> = ({
    runtimeOS
}) => {

    // =====================================================
    // State
    // =====================================================

    const [

        windows,

        setWindows

    ] = useState<
        RuntimeWindow[]
    >([])

    const [

        metrics,

        setMetrics

    ] = useState(
        runtimeOS.getMetrics()
    )

    // =====================================================
    // Refresh Loop
    // =====================================================

    useEffect(() => {

        let mounted = true

        const refresh = () => {

            if (!mounted) {

                return
            }

            setWindows(

                runtimeOS
                    .windowManager
                    .getWindows()
            )

            setMetrics(

                runtimeOS
                    .getMetrics()
            )
        }

        refresh()

        const interval =
            window.setInterval(

                refresh,

                250
            )

        return () => {

            mounted = false

            window.clearInterval(
                interval
            )
        }

    }, [runtimeOS])

    // =====================================================
    // Sorted Windows
    // =====================================================

    const sortedWindows =
        useMemo(() => {

            return [

                ...windows

            ].sort(

                (
                    a,
                    b
                ) => {

                    const af =
                        a.focused
                            ? 1
                            : 0

                    const bf =
                        b.focused
                            ? 1
                            : 0

                    return bf - af
                }
            )

        }, [windows])

    // =====================================================
    // Render
    // =====================================================

    return (

        <div
            className="
                fixed
                inset-0
                overflow-hidden
                bg-black
                text-white
            "
        >

            {/* =================================================
                Background
            ================================================== */}

            <div
                className="
                    absolute
                    inset-0
                    opacity-20
                "
                style={{
                    backgroundImage: `
                        radial-gradient(
                            circle at center,
                            rgba(34,211,238,0.10),
                            transparent 70%
                        )
                    `
                }}
            />

            {/* =================================================
                Grid
            ================================================== */}

            <div
                className="
                    absolute
                    inset-0
                    opacity-[0.05]
                "
                style={{
                    backgroundImage: `
                        linear-gradient(
                            to right,
                            white 1px,
                            transparent 1px
                        ),
                        linear-gradient(
                            to bottom,
                            white 1px,
                            transparent 1px
                        )
                    `,
                    backgroundSize:
                        "32px 32px"
                }}
            />

            {/* =================================================
                Runtime Status
            ================================================== */}

            <div
                className="
                    absolute
                    top-4
                    right-4
                    z-[9999]
                    rounded-xl
                    border
                    border-cyan-950
                    bg-black/70
                    backdrop-blur-md
                    px-4
                    py-3
                    flex
                    flex-col
                    gap-1
                    text-[10px]
                    font-mono
                "
            >

                <div
                    className="
                        text-cyan-300
                    "
                >
                    RuntimeOS
                </div>

                <div
                    className="
                        text-neutral-500
                    "
                >
                    runtimeEvents:
                    {" "}
                    {
                        metrics.sockets.runtimeEvents
                    }
                </div>

                <div
                    className="
                        text-neutral-500
                    "
                >
                    windows:
                    {" "}
                    {
                        metrics.windows.windows
                    }
                </div>

                <div
                    className="
                        text-neutral-500
                    "
                >
                    graphNodes:
                    {" "}
                    {
                        metrics.store.graphNodes
                    }
                </div>

            </div>

            {/* =================================================
                Windows
            ================================================== */}

            {
                sortedWindows.map(

                    (
                        runtimeWindow
                    ) => (

                        <RuntimeDesktopWindow
                            key={
                                runtimeWindow.id
                            }
                            runtimeOS={
                                runtimeOS
                            }
                            runtimeWindow={
                                runtimeWindow
                            }
                        />
                    )
                )
            }

        </div>
    )
}

// =========================================================
// Desktop Window
// =========================================================

interface RuntimeDesktopWindowProps {

    runtimeOS: RuntimeOS

    runtimeWindow: RuntimeWindow
}

// =========================================================
// RuntimeDesktopWindow
// =========================================================

const RuntimeDesktopWindow:
React.FC<
    RuntimeDesktopWindowProps
> = ({

    runtimeOS,

    runtimeWindow

}) => {

    if (
        runtimeWindow.minimized
    ) {

        return null
    }

    return (

        <div
            className={`
                absolute
                overflow-hidden
                rounded-2xl
                border
                backdrop-blur-xl
                transition-all
                ${
                    runtimeWindow.focused

                        ? `
                            border-cyan-500/40
                            shadow-[0_0_50px_rgba(34,211,238,0.18)]
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

                background:
                    "rgba(0,0,0,0.82)"
            }}
            onMouseDown={() => {

                runtimeOS
                    .windowManager
                    .focusWindow(
                        runtimeWindow.id
                    )
            }}
        >

            {/* =============================================
                Title Bar
            ============================================== */}

            <div
                className="
                    h-12
                    border-b
                    border-neutral-800
                    bg-black/70
                    backdrop-blur-md
                    px-4
                    flex
                    items-center
                    justify-between
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
                            font-semibold
                            text-cyan-300
                        "
                    >
                        {
                            runtimeWindow.title
                        }
                    </div>

                    <div
                        className="
                            text-[10px]
                            font-mono
                            text-neutral-500
                        "
                    >
                        {
                            runtimeWindow.applicationId
                        }
                    </div>

                </div>

                <div
                    className="
                        flex
                        items-center
                        gap-2
                    "
                >

                    <button
                        onClick={() => {

                            runtimeOS
                                .windowManager
                                .minimizeWindow(
                                    runtimeWindow.id
                                )
                        }}
                        className="
                            w-3
                            h-3
                            rounded-full
                            bg-yellow-500
                        "
                    />

                    <button
                        onClick={() => {

                            runtimeOS
                                .windowManager
                                .maximizeWindow(
                                    runtimeWindow.id
                                )
                        }}
                        className="
                            w-3
                            h-3
                            rounded-full
                            bg-green-500
                        "
                    />

                    <button
                        onClick={() => {

                            runtimeOS
                                .windowManager
                                .closeWindow(
                                    runtimeWindow.id
                                )
                        }}
                        className="
                            w-3
                            h-3
                            rounded-full
                            bg-red-500
                        "
                    />

                </div>

            </div>

            {/* =============================================
                Content
            ============================================== */}

            <div
                className="
                    absolute
                    inset-x-0
                    bottom-0
                    top-12
                    overflow-hidden
                "
            >

                <RuntimeWindowContent
                    runtimeOS={
                        runtimeOS
                    }
                    applicationId={
                        runtimeWindow.applicationId
                    }
                />

            </div>

        </div>
    )
}

// =========================================================
// Default Export
// =========================================================

export default RuntimeDesktop