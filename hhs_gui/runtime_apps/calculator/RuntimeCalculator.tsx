import React, {
    useMemo,
    useState
} from "react"

export interface RuntimeCalculatorProps {

    initialExpression?: string
}

export interface RuntimeCalculation {

    expression: string

    result: string

    timestamp: number
}

export const RuntimeCalculator: React.FC<
    RuntimeCalculatorProps
> = ({
    initialExpression = ""
}) => {

    const [
        expression,
        setExpression
    ] = useState(
        initialExpression
    )

    const [
        history,
        setHistory
    ] = useState<
        RuntimeCalculation[]
    >([])

    /**
     * ---------------------------------------------------
     * Runtime Evaluation
     * ---------------------------------------------------
     */

    const result = useMemo(() => {

        if (!expression.trim()) {

            return ""
        }

        try {

            /**
             * ------------------------------------------------
             * Placeholder evaluation layer
             * ------------------------------------------------
             *
             * Replace later with:
             *
             * - HHS parser
             * - VM81 runtime bridge
             * - symbolic manifold evaluator
             * - replay-linked execution
             * - tensor reduction engine
             */

            const evaluated =
                Function(
                    `"use strict";
                    return (${expression})
                    `
                )()

            return String(
                evaluated
            )
        }
        catch {

            return "ERR"
        }

    }, [expression])

    /**
     * ---------------------------------------------------
     * Commit Calculation
     * ---------------------------------------------------
     */

    const commitCalculation =
        () => {

            if (
                !expression.trim()
            ) {

                return
            }

            setHistory((prev) => [

                {

                    expression,

                    result,

                    timestamp:
                        Date.now()
                },

                ...prev
            ])
        }

    /**
     * ---------------------------------------------------
     * Render
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                w-full
                h-full
                flex
                flex-col
                bg-neutral-950
                text-neutral-100
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
                    px-4
                    flex
                    items-center
                    justify-between
                    shrink-0
                    bg-neutral-900
                "
            >

                <div
                    className="
                        font-semibold
                        tracking-wide
                    "
                >
                    Runtime Calculator
                </div>

                <div
                    className="
                        text-xs
                        opacity-50
                        font-mono
                    "
                >
                    VM81 symbolic execution
                </div>

            </div>

            {/* -------------------------------- */}
            {/* Expression Surface */}
            {/* -------------------------------- */}

            <div
                className="
                    p-4
                    border-b
                    border-neutral-800
                    flex
                    flex-col
                    gap-4
                    shrink-0
                "
            >

                <textarea
                    value={expression}
                    onChange={(event) =>
                        setExpression(
                            event.target.value
                        )
                    }
                    placeholder="
                        Enter manifold expression...
                    "
                    className="
                        w-full
                        min-h-[120px]
                        rounded-xl
                        border
                        border-neutral-800
                        bg-neutral-900
                        p-4
                        font-mono
                        text-sm
                        resize-none
                        outline-none
                    "
                />

                <div
                    className="
                        flex
                        items-center
                        gap-3
                    "
                >

                    <button
                        onClick={
                            commitCalculation
                        }
                        className="
                            px-4
                            py-2
                            rounded-lg
                            bg-cyan-600
                            hover:bg-cyan-500
                            transition
                            text-sm
                            font-semibold
                        "
                    >
                        Execute
                    </button>

                    <button
                        onClick={() => {

                            setExpression("")
                        }}
                        className="
                            px-4
                            py-2
                            rounded-lg
                            bg-neutral-800
                            hover:bg-neutral-700
                            transition
                            text-sm
                        "
                    >
                        Clear
                    </button>

                </div>

            </div>

            {/* -------------------------------- */}
            {/* Result Surface */}
            {/* -------------------------------- */}

            <div
                className="
                    p-4
                    border-b
                    border-neutral-800
                    flex
                    flex-col
                    gap-3
                    shrink-0
                "
            >

                <div
                    className="
                        text-xs
                        opacity-50
                        font-mono
                    "
                >
                    RESULT
                </div>

                <div
                    className="
                        rounded-xl
                        border
                        border-neutral-800
                        bg-black
                        p-4
                        font-mono
                        text-lg
                        min-h-[80px]
                        flex
                        items-center
                    "
                >
                    {result}
                </div>

            </div>

            {/* -------------------------------- */}
            {/* History */}
            {/* -------------------------------- */}

            <div
                className="
                    flex-1
                    overflow-auto
                    p-4
                    flex
                    flex-col
                    gap-3
                "
            >

                <div
                    className="
                        text-xs
                        opacity-50
                        font-mono
                    "
                >
                    EXECUTION HISTORY
                </div>

                {
                    history.map((item) => (

                        <div
                            key={
                                item.timestamp
                            }
                            className="
                                rounded-xl
                                border
                                border-neutral-800
                                bg-neutral-900
                                p-4
                                flex
                                flex-col
                                gap-2
                            "
                        >

                            <div
                                className="
                                    text-xs
                                    opacity-50
                                    font-mono
                                "
                            >
                                {
                                    new Date(
                                        item.timestamp
                                    ).toLocaleTimeString()
                                }
                            </div>

                            <div
                                className="
                                    font-mono
                                    text-sm
                                    break-all
                                "
                            >
                                {
                                    item.expression
                                }
                            </div>

                            <div
                                className="
                                    text-cyan-400
                                    font-mono
                                    text-sm
                                    break-all
                                "
                            >
                                →
                                {" "}
                                {
                                    item.result
                                }
                            </div>

                        </div>
                    ))
                }

            </div>

        </div>
    )
}