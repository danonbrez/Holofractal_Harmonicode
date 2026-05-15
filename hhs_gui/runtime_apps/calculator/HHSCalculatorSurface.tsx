import React, {
    useCallback,
    useMemo,
    useState
} from "react"

// =========================================================
// Types
// =========================================================

interface SolveResponse {

    status: string

    runtime_id?: string

    branch_id?: string

    event_hash72?: string

    receipt_hash72?: string

    payload?: unknown
}

// =========================================================
// Constants
// =========================================================

const DEFAULT_EXPRESSION =
    "(x/y)(y/x)==1"

// =========================================================
// HHSCalculatorSurface
// =========================================================

export const HHSCalculatorSurface:
React.FC = () => {

    // =====================================================
    // State
    // =====================================================

    const [

        expression,

        setExpression

    ] = useState(
        DEFAULT_EXPRESSION
    )

    const [

        loading,

        setLoading

    ] = useState(false)

    const [

        error,

        setError

    ] = useState<
        string | null
    >(null)

    const [

        response,

        setResponse

    ] = useState<
        SolveResponse | null
    >(null)

    // =====================================================
    // Runtime Endpoint
    // =====================================================

    const runtimeEndpoint =
        useMemo(() => {

            return (

                `${window.location.origin}`

                +

                `/api/hhs/solve`
            )

        }, [])

    // =====================================================
    // Solve
    // =====================================================

    const solveExpression =
        useCallback(
            async () => {

                setLoading(true)

                setError(null)

                try {

                    const result =
                        await fetch(

                            runtimeEndpoint,

                            {

                                method: "POST",

                                headers: {

                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({

                                    expression,

                                    runtime_id:
                                        "runtime_main",

                                    branch_id:
                                        "main"
                                })
                            }
                        )

                    if (
                        !result.ok
                    ) {

                        throw new Error(

                            `Runtime request failed (${result.status})`
                        )
                    }

                    const json =
                        await result.json()

                    setResponse(json)

                } catch (error) {

                    console.error(

                        "[HHSCalculatorSurface] runtime solve failure",

                        error
                    )

                    setError(

                        error instanceof Error

                            ? error.message

                            : "Unknown runtime error"
                    )

                } finally {

                    setLoading(false)
                }
            },

            [

                expression,

                runtimeEndpoint
            ]
        )

    // =====================================================
    // Render
    // =====================================================

    return (

        <div
            className="
                w-full
                h-full
                bg-neutral-950
                text-white
                overflow-hidden
                flex
                flex-col
            "
        >

            {/* =================================================
                Header
            ================================================== */}

            <div
                className="
                    border-b
                    border-neutral-800
                    px-4
                    py-3
                    flex
                    items-center
                    justify-between
                    bg-black/60
                    backdrop-blur-md
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
                            text-cyan-300
                            text-sm
                            font-semibold
                        "
                    >
                        HHS Runtime Calculator
                    </div>

                    <div
                        className="
                            text-neutral-500
                            text-[10px]
                            font-mono
                        "
                    >
                        runtime_execution_surface
                    </div>

                </div>

                <button
                    onClick={
                        solveExpression
                    }
                    disabled={
                        loading
                    }
                    className="
                        px-4
                        py-2
                        rounded-lg
                        bg-cyan-500/20
                        border
                        border-cyan-500/30
                        text-cyan-300
                        text-sm
                        font-medium
                        hover:bg-cyan-500/30
                        transition-colors
                        disabled:opacity-40
                    "
                >

                    {
                        loading

                            ? "Executing..."

                            : "Execute"
                    }

                </button>

            </div>

            {/* =================================================
                Expression Input
            ================================================== */}

            <div
                className="
                    p-4
                    border-b
                    border-neutral-900
                "
            >

                <textarea
                    value={
                        expression
                    }
                    onChange={(event) => {

                        setExpression(
                            event.target.value
                        )
                    }}
                    spellCheck={false}
                    className="
                        w-full
                        min-h-[160px]
                        rounded-xl
                        border
                        border-neutral-800
                        bg-black
                        text-cyan-300
                        p-4
                        font-mono
                        text-sm
                        resize-none
                        outline-none
                        focus:border-cyan-500/40
                    "
                />

            </div>

            {/* =================================================
                Runtime Status
            ================================================== */}

            <div
                className="
                    px-4
                    py-3
                    border-b
                    border-neutral-900
                    flex
                    items-center
                    gap-3
                    text-xs
                    font-mono
                "
            >

                <div
                    className="
                        text-cyan-500
                    "
                >
                    runtime:
                </div>

                <div
                    className="
                        text-neutral-400
                    "
                >
                    api_runtime_projection
                </div>

            </div>

            {/* =================================================
                Error
            ================================================== */}

            {
                error && (

                    <div
                        className="
                            m-4
                            rounded-xl
                            border
                            border-red-900
                            bg-red-950/40
                            p-4
                            text-red-300
                            text-sm
                            font-mono
                        "
                    >

                        {error}

                    </div>
                )
            }

            {/* =================================================
                Response
            ================================================== */}

            <div
                className="
                    flex-1
                    overflow-auto
                    p-4
                "
            >

                <div
                    className="
                        rounded-2xl
                        border
                        border-neutral-800
                        bg-black/40
                        overflow-hidden
                    "
                >

                    <div
                        className="
                            border-b
                            border-neutral-800
                            px-4
                            py-3
                            text-sm
                            font-semibold
                            text-cyan-300
                        "
                    >
                        Runtime Response
                    </div>

                    <pre
                        className="
                            p-4
                            text-xs
                            text-neutral-300
                            font-mono
                            whitespace-pre-wrap
                            break-all
                            overflow-auto
                        "
                    >
                        {
                            JSON.stringify(

                                response,

                                null,

                                2
                            )
                        }
                    </pre>

                </div>

            </div>

        </div>
    )
}

// =========================================================
// Default Export
// =========================================================

export default HHSCalculatorSurface