import React, {
    useCallback,
    useEffect,
    useRef,
    useState
} from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

// =========================================================
// Types
// =========================================================

interface RuntimeCommandReceipt {

    expression: string

    timestamp: number

    status: "success" | "error"

    response?: unknown

    error?: string
}

// =========================================================
// Props
// =========================================================

export interface RuntimeCommandBarProps {

    runtimeOS: RuntimeOS
}

// =========================================================
// RuntimeCommandBar
// =========================================================

export const RuntimeCommandBar: React.FC<
    RuntimeCommandBarProps
> = ({
    runtimeOS
}) => {

    const inputRef =
        useRef<HTMLInputElement>(
            null
        )

    const [expression, setExpression] =
        useState("")

    const [executing, setExecuting] =
        useState(false)

    const [mode, setMode] =
        useState<
            "evaluate"
            | "agent"
        >("evaluate")

    const [history, setHistory] =
        useState<
            RuntimeCommandReceipt[]
        >([])

    const [historyIndex, setHistoryIndex] =
        useState(-1)

    // =====================================================
    // Focus
    // =====================================================

    useEffect(() => {

        const handler = (
            event: KeyboardEvent
        ) => {

            /**
             * -------------------------------------------------
             * Global Runtime Shortcut
             * -------------------------------------------------
             *
             * CTRL + K
             */

            if (

                event.ctrlKey
                &&
                event.key
                    .toLowerCase()
                    === "k"

            ) {

                event.preventDefault()

                inputRef.current?.focus()
            }
        }

        window.addEventListener(
            "keydown",
            handler
        )

        return () => {

            window.removeEventListener(
                "keydown",
                handler
            )
        }

    }, [])

    // =====================================================
    // Execute
    // =====================================================

    const execute =
        useCallback(
            async () => {

                const trimmed =
                    expression.trim()

                if (
                    !trimmed
                ) {

                    return
                }

                setExecuting(true)

                try {

                    const endpoint =

                        mode
                        === "agent"

                            ? "/api/agent/run-loop"

                            : "/api/calculator/evaluate"

                    const payload =

                        mode
                        === "agent"

                            ? {

                                expression:
                                    trimmed,

                                auto_continue:
                                    true,

                                max_passes:
                                    3
                            }

                            : {

                                expression:
                                    trimmed
                            }

                    const response =
                        await fetch(

                            endpoint,

                            {

                                method: "POST",

                                headers: {

                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify(
                                        payload
                                    )
                            }
                        )

                    if (
                        !response.ok
                    ) {

                        throw new Error(

                            `HTTP ${response.status}`
                        )
                    }

                    const data =
                        await response.json()

                    const receipt:
                        RuntimeCommandReceipt = {

                        expression:
                            trimmed,

                        timestamp:
                            Date.now(),

                        status:
                            "success",

                        response:
                            data
                    }

                    setHistory(
                        (previous) => [

                            receipt,

                            ...previous
                        ]
                    )

                    setExpression("")

                    setHistoryIndex(-1)

                    console.log(

                        "[RuntimeCommandBar] execute",

                        data
                    )

                } catch (error) {

                    const receipt:
                        RuntimeCommandReceipt = {

                        expression:
                            trimmed,

                        timestamp:
                            Date.now(),

                        status:
                            "error",

                        error:
                            error instanceof Error

                                ? error.message

                                : "unknown_error"
                    }

                    setHistory(
                        (previous) => [

                            receipt,

                            ...previous
                        ]
                    )

                    console.error(

                        "[RuntimeCommandBar] execute failure",

                        error
                    )

                } finally {

                    setExecuting(false)
                }

            },

            [

                expression,

                mode
            ]
        )

    // =====================================================
    // History Navigation
    // =====================================================

    const navigateHistory =
        useCallback(

            (
                direction:
                    "up"
                    | "down"
            ) => {

                if (
                    history.length
                    === 0
                ) {

                    return
                }

                let nextIndex =
                    historyIndex

                if (
                    direction
                    === "up"
                ) {

                    nextIndex = Math.min(

                        history.length - 1,

                        historyIndex + 1
                    )

                } else {

                    nextIndex = Math.max(

                        -1,

                        historyIndex - 1
                    )
                }

                setHistoryIndex(
                    nextIndex
                )

                if (
                    nextIndex === -1
                ) {

                    setExpression("")

                    return
                }

                setExpression(

                    history[
                        nextIndex
                    ].expression
                )

            },

            [

                history,

                historyIndex
            ]
        )

    // =====================================================
    // Keydown
    // =====================================================

    const onKeyDown =
        (
            event:
                React.KeyboardEvent
        ) => {

            if (
                event.key
                === "Enter"
            ) {

                event.preventDefault()

                execute()

                return
            }

            if (
                event.key
                === "ArrowUp"
            ) {

                event.preventDefault()

                navigateHistory("up")

                return
            }

            if (
                event.key
                === "ArrowDown"
            ) {

                event.preventDefault()

                navigateHistory("down")
            }
        }

    // =====================================================
    // Render
    // =====================================================

    return (

        <div
            className="
                absolute
                bottom-6
                left-1/2
                -translate-x-1/2
                z-[4000]
                w-[min(980px,92vw)]
            "
        >

            <div
                className="
                    rounded-2xl
                    border
                    border-neutral-800
                    bg-neutral-900/90
                    backdrop-blur-xl
                    shadow-2xl
                    overflow-hidden
                "
            >

                {/* ============================================= */}
                {/* Top Controls */}
                {/* ============================================= */}

                <div
                    className="
                        h-12
                        border-b
                        border-neutral-800
                        px-4
                        flex
                        items-center
                        justify-between
                        bg-neutral-950/80
                    "
                >

                    <div
                        className="
                            flex
                            items-center
                            gap-2
                        "
                    >

                        <button
                            onClick={() => {

                                setMode(
                                    "evaluate"
                                )
                            }}
                            className={`
                                px-3
                                py-1
                                rounded-lg
                                text-xs
                                font-medium
                                transition
                                ${
                                    mode === "evaluate"

                                        ? `
                                            bg-cyan-500/20
                                            text-cyan-300
                                            border
                                            border-cyan-500/30
                                        `

                                        : `
                                            bg-neutral-900
                                            text-neutral-400
                                            border
                                            border-neutral-800
                                        `
                                }
                            `}
                        >
                            evaluate
                        </button>

                        <button
                            onClick={() => {

                                setMode(
                                    "agent"
                                )
                            }}
                            className={`
                                px-3
                                py-1
                                rounded-lg
                                text-xs
                                font-medium
                                transition
                                ${
                                    mode === "agent"

                                        ? `
                                            bg-purple-500/20
                                            text-purple-300
                                            border
                                            border-purple-500/30
                                        `

                                        : `
                                            bg-neutral-900
                                            text-neutral-400
                                            border
                                            border-neutral-800
                                        `
                                }
                            `}
                        >
                            agent
                        </button>

                    </div>

                    <div
                        className="
                            text-[10px]
                            uppercase
                            tracking-[0.2em]
                            text-neutral-500
                            font-mono
                        "
                    >
                        ctrl+k
                    </div>

                </div>

                {/* ============================================= */}
                {/* Input */}
                {/* ============================================= */}

                <div
                    className="
                        flex
                        items-center
                        gap-3
                        px-4
                        py-4
                    "
                >

                    <div
                        className="
                            text-cyan-400
                            font-mono
                            text-sm
                            shrink-0
                        "
                    >
                        λ
                    </div>

                    <input
                        ref={inputRef}
                        value={expression}
                        onChange={(e) => {

                            setExpression(
                                e.target.value
                            )
                        }}
                        onKeyDown={onKeyDown}
                        placeholder={
                            mode === "agent"

                                ? `
                                    execute runtime agent loop
                                  `

                                : `
                                    evaluate runtime expression
                                  `
                        }
                        className="
                            flex-1
                            bg-transparent
                            outline-none
                            text-white
                            font-mono
                            text-sm
                            placeholder:text-neutral-600
                        "
                    />

                    <button
                        disabled={executing}
                        onClick={() => {

                            execute()
                        }}
                        className={`
                            px-4
                            py-2
                            rounded-xl
                            text-sm
                            font-medium
                            transition
                            ${
                                executing

                                    ? `
                                        bg-neutral-800
                                        text-neutral-500
                                      `

                                    : `
                                        bg-cyan-500/20
                                        text-cyan-300
                                        border
                                        border-cyan-500/30
                                        hover:bg-cyan-500/30
                                      `
                            }
                        `}
                    >

                        {
                            executing

                                ? "running"

                                : "execute"
                        }

                    </button>

                </div>

                {/* ============================================= */}
                {/* History */}
                {/* ============================================= */}

                {
                    history.length > 0 && (

                        <div
                            className="
                                border-t
                                border-neutral-800
                                max-h-[220px]
                                overflow-auto
                            "
                        >

                            {
                                history
                                    .slice(0, 12)
                                    .map(

                                        (
                                            entry,
                                            index
                                        ) => (

                                            <div
                                                key={index}
                                                className="
                                                    px-4
                                                    py-3
                                                    border-b
                                                    border-neutral-900
                                                    font-mono
                                                    text-xs
                                                "
                                            >

                                                <div
                                                    className="
                                                        flex
                                                        items-center
                                                        justify-between
                                                        gap-4
                                                    "
                                                >

                                                    <div
                                                        className="
                                                            break-all
                                                            text-neutral-300
                                                        "
                                                    >
                                                        {
                                                            entry.expression
                                                        }
                                                    </div>

                                                    <div
                                                        className={`
                                                            shrink-0
                                                            uppercase
                                                            tracking-wide
                                                            text-[10px]
                                                            ${
                                                                entry.status
                                                                === "success"

                                                                    ? "text-green-400"

                                                                    : "text-red-400"
                                                            }
                                                        `}
                                                    >
                                                        {
                                                            entry.status
                                                        }
                                                    </div>

                                                </div>

                                                {
                                                    entry.error && (

                                                        <div
                                                            className="
                                                                mt-2
                                                                text-red-400
                                                                break-all
                                                            "
                                                        >
                                                            {
                                                                entry.error
                                                            }
                                                        </div>
                                                    )
                                                }

                                            </div>
                                        )
                                    )
                            }

                        </div>
                    )
                }

            </div>

        </div>
    )
}