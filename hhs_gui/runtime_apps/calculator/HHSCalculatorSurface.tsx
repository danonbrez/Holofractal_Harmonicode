import React, { useMemo, useState } from "react"

import {
    RuntimeExecutionAuthority
} from "../../runtime_os/core/RuntimeExecutionAuthority"

/**
 * HHS Calculator Surface
 * ---------------------------------------------------
 * Kernel-authorized symbolic calculator projection.
 *
 * CRITICAL:
 *
 * This component does NOT:
 *
 * - evaluate expressions locally
 * - parse algebra locally
 * - simplify equations locally
 * - mutate graph state locally
 * - generate receipts locally
 * - generate replay chains locally
 *
 * All execution routes through:
 *
 * GUI
 * → RuntimeExecutionAuthority
 * → RuntimeKernelBridge
 * → Canonical Runtime
 * → Kernel
 * → Receipt Commit
 * → Replay
 * → Projection
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface HHSCalculatorSurfaceProps {

    authority: RuntimeExecutionAuthority
}

export interface CalculatorExecutionRecord {

    id: string

    expression: string

    timestamp: number

    accepted: boolean

    authorityPath: string[]

    receiptRequired: boolean

    replayLinked: boolean
}

const DEFAULT_EXPRESSION = `
P² - pq = n⁴ = xy

A = P² = B

xy = 1
yx = -1

R_K^{QGU} = (xy + cq² + dq⁴) / (xy + cq²)
`.trim()

export const HHSCalculatorSurface:
React.FC<
    HHSCalculatorSurfaceProps
> = ({
    authority
}) => {

    const [expression, setExpression] =
        useState(DEFAULT_EXPRESSION)

    const [history, setHistory] =
        useState<CalculatorExecutionRecord[]>([])

    const [selectedRecordId, setSelectedRecordId] =
        useState<string | null>(null)

    /**
     * ---------------------------------------------------
     * Selected Record
     * ---------------------------------------------------
     */

    const selectedRecord =
        useMemo(() => {

            if (!selectedRecordId) {

                return undefined
            }

            return history.find(

                (record) =>
                    record.id === selectedRecordId
            )

        }, [
            history,
            selectedRecordId
        ])

    /**
     * ---------------------------------------------------
     * Kernel Execution Dispatch
     * ---------------------------------------------------
     */

    const executeExpression = () => {

        const trimmed =
            expression.trim()

        if (!trimmed) {

            return
        }

        const receipt =
            authority.execute({

                operation:
                    "calculator.evaluate_expression",

                payload: {

                    expression:
                        trimmed,

                    inputType:
                        "hhs_symbolic_constraint",

                    projectionMode:
                        "calculator_surface"
                },

                requiresReceipt:
                    true,

                requiresReplayLink:
                    true,

                sourceComponent:
                    "HHSCalculatorSurface"
            })

        const record:
            CalculatorExecutionRecord = {

            id:
                crypto.randomUUID(),

            expression:
                trimmed,

            timestamp:
                Date.now(),

            accepted:
                receipt.accepted,

            authorityPath:
                receipt.authorityPath,

            receiptRequired:
                receipt.receiptRequired,

            replayLinked:
                receipt.replayLinked
        }

        setHistory((previous) => [

            record,

            ...previous
        ])

        setSelectedRecordId(
            record.id
        )
    }

    /**
     * ---------------------------------------------------
     * Export Projection Object
     * ---------------------------------------------------
     */

    const buildProjectionObject = () => {

        return {

            object_type:
                "hhs_calculator_projection",

            expression,

            selected_record:
                selectedRecord,

            execution_authority:
                authority.serialize(),

            exported_at:
                Date.now(),

            invariant_status: {

                delta_e:
                    0,

                psi:
                    0,

                theta15:
                    true,

                omega:
                    true
            }
        }
    }

    const copyProjectionJson = async () => {

        const projection =
            buildProjectionObject()

        await navigator.clipboard.writeText(

            JSON.stringify(
                projection,
                null,
                2
            )
        )
    }

    /**
     * ---------------------------------------------------
     * Surface
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                w-full
                h-full
                bg-neutral-950
                text-neutral-100
                flex
                overflow-hidden
            "
        >

            {/* -------------------------------- */}
            {/* Input Panel */}
            {/* -------------------------------- */}

            <div
                className="
                    w-1/2
                    h-full
                    border-r
                    border-neutral-800
                    flex
                    flex-col
                "
            >

                <div
                    className="
                        h-14
                        border-b
                        border-neutral-800
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
                                font-semibold
                                text-cyan-300
                            "
                        >
                            HHS Calculator
                        </div>

                        <div
                            className="
                                text-[10px]
                                opacity-50
                                font-mono
                            "
                        >
                            kernel-authorized symbolic projection
                        </div>

                    </div>

                    <button

                        onClick={executeExpression}

                        className="
                            px-4
                            py-2
                            rounded-lg
                            bg-cyan-500/20
                            border
                            border-cyan-500
                            text-cyan-200
                            text-xs
                            font-mono
                            hover:bg-cyan-500/30
                            transition
                        "
                    >
                        EXECUTE VIA KERNEL
                    </button>

                </div>

                <textarea

                    value={expression}

                    onChange={(event) => {

                        setExpression(
                            event.target.value
                        )
                    }}

                    spellCheck={false}

                    className="
                        flex-1
                        bg-black
                        text-green-300
                        font-mono
                        text-sm
                        p-5
                        outline-none
                        resize-none
                    "
                />

                <div
                    className="
                        h-12
                        border-t
                        border-neutral-800
                        flex
                        items-center
                        justify-between
                        px-4
                        text-[10px]
                        font-mono
                        opacity-60
                    "
                >

                    <div>
                        local algebra disabled
                    </div>

                    <div>
                        authority locked
                    </div>

                    <div>
                        receipt required
                    </div>

                </div>

            </div>

            {/* -------------------------------- */}
            {/* Projection Panel */}
            {/* -------------------------------- */}

            <div
                className="
                    w-1/2
                    h-full
                    flex
                    flex-col
                    bg-neutral-950
                "
            >

                <div
                    className="
                        h-14
                        border-b
                        border-neutral-800
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
                                font-semibold
                            "
                        >
                            Runtime Projection
                        </div>

                        <div
                            className="
                                text-[10px]
                                opacity-50
                                font-mono
                            "
                        >
                            receipt / replay / authority path
                        </div>

                    </div>

                    <button

                        onClick={copyProjectionJson}

                        className="
                            px-3
                            py-2
                            rounded-lg
                            border
                            border-neutral-700
                            bg-neutral-900
                            hover:bg-neutral-800
                            transition
                            text-xs
                            font-mono
                        "
                    >
                        COPY JSON
                    </button>

                </div>

                {/* ---------------------------- */}
                {/* Selected Record */}
                {/* ---------------------------- */}

                <div
                    className="
                        flex-1
                        overflow-auto
                        p-4
                        flex
                        flex-col
                        gap-4
                    "
                >

                    {
                        selectedRecord ? (

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
                                        px-4
                                        py-3
                                        border-b
                                        border-neutral-800
                                        flex
                                        items-center
                                        justify-between
                                    "
                                >

                                    <div
                                        className="
                                            text-sm
                                            font-semibold
                                            text-cyan-300
                                        "
                                    >
                                        Execution Record
                                    </div>

                                    <div
                                        className={`
                                            text-[10px]
                                            font-mono
                                            px-2
                                            py-1
                                            rounded
                                            border

                                            ${
                                                selectedRecord.accepted
                                                    ? `
                                                        border-green-500
                                                        text-green-300
                                                        bg-green-500/10
                                                      `
                                                    : `
                                                        border-red-500
                                                        text-red-300
                                                        bg-red-500/10
                                                      `
                                            }
                                        `}
                                    >
                                        {
                                            selectedRecord.accepted
                                                ? "ACCEPTED"
                                                : "REJECTED"
                                        }
                                    </div>

                                </div>

                                <div
                                    className="
                                        p-4
                                        flex
                                        flex-col
                                        gap-4
                                    "
                                >

                                    <div
                                        className="
                                            text-[10px]
                                            font-mono
                                            opacity-60
                                        "
                                    >
                                        {new Date(
                                            selectedRecord.timestamp
                                        ).toISOString()}
                                    </div>

                                    <pre
                                        className="
                                            p-4
                                            rounded-xl
                                            bg-neutral-900
                                            text-green-300
                                            text-xs
                                            overflow-auto
                                            whitespace-pre-wrap
                                        "
                                    >
                                        {
                                            selectedRecord.expression
                                        }
                                    </pre>

                                    <div
                                        className="
                                            grid
                                            grid-cols-2
                                            gap-3
                                            text-[10px]
                                            font-mono
                                        "
                                    >

                                        <div
                                            className="
                                                p-3
                                                rounded-xl
                                                bg-neutral-900
                                                border
                                                border-neutral-800
                                            "
                                        >
                                            receiptRequired:
                                            {" "}
                                            {
                                                String(
                                                    selectedRecord
                                                        .receiptRequired
                                                )
                                            }
                                        </div>

                                        <div
                                            className="
                                                p-3
                                                rounded-xl
                                                bg-neutral-900
                                                border
                                                border-neutral-800
                                            "
                                        >
                                            replayLinked:
                                            {" "}
                                            {
                                                String(
                                                    selectedRecord
                                                        .replayLinked
                                                )
                                            }
                                        </div>

                                    </div>

                                    <div
                                        className="
                                            rounded-xl
                                            border
                                            border-neutral-800
                                            bg-neutral-900
                                            p-4
                                        "
                                    >

                                        <div
                                            className="
                                                text-xs
                                                font-semibold
                                                mb-3
                                            "
                                        >
                                            Authority Path
                                        </div>

                                        <div
                                            className="
                                                flex
                                                flex-col
                                                gap-2
                                            "
                                        >

                                            {
                                                selectedRecord
                                                    .authorityPath
                                                    .map(
                                                        (
                                                            item,
                                                            index
                                                        ) => (

                                                            <div
                                                                key={`${item}-${index}`}
                                                                className="
                                                                    flex
                                                                    items-center
                                                                    gap-2
                                                                    text-[10px]
                                                                    font-mono
                                                                "
                                                            >

                                                                <div
                                                                    className="
                                                                        w-6
                                                                        h-6
                                                                        rounded-full
                                                                        bg-cyan-500/20
                                                                        border
                                                                        border-cyan-500
                                                                        flex
                                                                        items-center
                                                                        justify-center
                                                                        text-cyan-300
                                                                    "
                                                                >
                                                                    {
                                                                        index + 1
                                                                    }
                                                                </div>

                                                                <div>
                                                                    {item}
                                                                </div>

                                                            </div>
                                                        )
                                                    )
                                            }

                                        </div>

                                    </div>

                                </div>

                            </div>

                        ) : (

                            <div
                                className="
                                    flex-1
                                    flex
                                    items-center
                                    justify-center
                                    text-sm
                                    opacity-50
                                    font-mono
                                "
                            >
                                No kernel execution record selected.
                            </div>
                        )
                    }

                </div>

                {/* ---------------------------- */}
                {/* History */}
                {/* ---------------------------- */}

                <div
                    className="
                        h-48
                        border-t
                        border-neutral-800
                        overflow-auto
                    "
                >

                    <div
                        className="
                            px-4
                            py-2
                            text-xs
                            font-semibold
                            border-b
                            border-neutral-800
                        "
                    >
                        Execution History
                    </div>

                    {
                        history.map((record) => (

                            <button

                                key={record.id}

                                onClick={() => {

                                    setSelectedRecordId(
                                        record.id
                                    )
                                }}

                                className={`
                                    w-full
                                    px-4
                                    py-3
                                    border-b
                                    border-neutral-900
                                    text-left
                                    hover:bg-neutral-900
                                    transition

                                    ${
                                        selectedRecordId === record.id
                                            ? "bg-cyan-500/10"
                                            : ""
                                    }
                                `}
                            >

                                <div
                                    className="
                                        text-xs
                                        font-mono
                                        truncate
                                    "
                                >
                                    {
                                        record.expression
                                            .split("\n")[0]
                                    }
                                </div>

                                <div
                                    className="
                                        text-[10px]
                                        opacity-50
                                        font-mono
                                        mt-1
                                    "
                                >
                                    {
                                        record.accepted
                                            ? "accepted"
                                            : "rejected"
                                    }
                                    {" "}
                                    · replay:
                                    {" "}
                                    {
                                        String(
                                            record.replayLinked
                                        )
                                    }
                                </div>

                            </button>
                        ))
                    }

                </div>

            </div>

        </div>
    )
}