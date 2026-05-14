import React, {
    useEffect,
    useMemo,
    useState
} from "react"

import type {
    RuntimeReceipt
} from "../../runtime_os/state/RuntimeStateStore"

import {
    RuntimeStateStore
} from "../../runtime_os/state/RuntimeStateStore"

// =========================================================
// Props
// =========================================================

export interface ReceiptInspectorProps {

    runtimeStore:
        RuntimeStateStore
}

// =========================================================
// ReceiptInspector
// =========================================================

const ReceiptInspector: React.FC<
    ReceiptInspectorProps
> = ({
    runtimeStore
}) => {

    const [receipts, setReceipts] =
        useState<RuntimeReceipt[]>(

            runtimeStore
                .getReceipts()
        )

    const [selectedReceipt, setSelectedReceipt] =
        useState<
            RuntimeReceipt
            | null
        >(null)

    const [search, setSearch] =
        useState("")

    // =====================================================
    // Runtime Subscription
    // =====================================================

    useEffect(() => {

        const unsubscribe =
            runtimeStore.subscribe(

                (state) => {

                    setReceipts(
                        [...state.receipts]
                    )
                }
            )

        return () => {

            unsubscribe()
        }

    }, [runtimeStore])

    // =====================================================
    // Filtered Receipts
    // =====================================================

    const filteredReceipts =
        useMemo(() => {

            if (!search.trim()) {

                return receipts
            }

            const needle =
                search.toLowerCase()

            return receipts.filter(

                (receipt) => (

                    receipt
                        .receipt_hash72
                        .toLowerCase()
                        .includes(needle)

                    ||

                    receipt
                        .source_hash72
                        .toLowerCase()
                        .includes(needle)

                    ||

                    receipt
                        .operation
                        .toLowerCase()
                        .includes(needle)
                )
            )

        }, [

            receipts,

            search
        ])

    // =====================================================
    // Render
    // =====================================================

    return (

        <div
            className="
                w-full
                h-full
                overflow-hidden
                bg-neutral-950
                text-white
                flex
            "
        >

            {/* ================================================= */}
            {/* Receipt List */}
            {/* ================================================= */}

            <div
                className="
                    w-[420px]
                    border-r
                    border-neutral-800
                    flex
                    flex-col
                    overflow-hidden
                "
            >

                {/* --------------------------------------------- */}
                {/* Header */}
                {/* --------------------------------------------- */}

                <div
                    className="
                        h-14
                        shrink-0
                        border-b
                        border-neutral-800
                        px-4
                        flex
                        items-center
                        justify-between
                        bg-neutral-900
                    "
                >

                    <div
                        className="
                            font-semibold
                            text-sm
                            tracking-wide
                        "
                    >
                        Receipt Inspector
                    </div>

                    <div
                        className="
                            text-xs
                            opacity-60
                            font-mono
                        "
                    >
                        {
                            filteredReceipts
                                .length
                        }
                        {" "}
                        receipts
                    </div>

                </div>

                {/* --------------------------------------------- */}
                {/* Search */}
                {/* --------------------------------------------- */}

                <div
                    className="
                        p-3
                        border-b
                        border-neutral-800
                        bg-neutral-900/50
                    "
                >

                    <input
                        value={search}
                        onChange={(e) => {

                            setSearch(
                                e.target.value
                            )
                        }}
                        placeholder="
                            search receipt / source / operation
                        "
                        className="
                            runtime-input
                            w-full
                            px-3
                            py-2
                            text-sm
                            font-mono
                        "
                    />

                </div>

                {/* --------------------------------------------- */}
                {/* Receipt Timeline */}
                {/* --------------------------------------------- */}

                <div
                    className="
                        flex-1
                        overflow-auto
                    "
                >

                    {
                        filteredReceipts
                            .slice()
                            .reverse()
                            .map(

                                (
                                    receipt,
                                    index
                                ) => {

                                    const active =

                                        selectedReceipt
                                        === receipt

                                    return (

                                        <button
                                            key={index}
                                            onClick={() => {

                                                setSelectedReceipt(
                                                    receipt
                                                )
                                            }}
                                            className={`
                                                w-full
                                                text-left
                                                px-4
                                                py-3
                                                border-b
                                                border-neutral-900
                                                transition
                                                hover:bg-neutral-900
                                                ${
                                                    active
                                                        ? "bg-neutral-900"
                                                        : ""
                                                }
                                            `}
                                        >

                                            <div
                                                className="
                                                    flex
                                                    items-center
                                                    justify-between
                                                    mb-1
                                                "
                                            >

                                                <div
                                                    className="
                                                        text-xs
                                                        text-cyan-400
                                                        font-mono
                                                    "
                                                >
                                                    {
                                                        receipt.operation
                                                    }
                                                </div>

                                                <div
                                                    className="
                                                        text-[10px]
                                                        opacity-40
                                                        uppercase
                                                    "
                                                >
                                                    {
                                                        receipt
                                                            .closure_class
                                                    }
                                                </div>

                                            </div>

                                            <div
                                                className="
                                                    text-[10px]
                                                    opacity-70
                                                    font-mono
                                                    break-all
                                                "
                                            >
                                                {
                                                    receipt
                                                        .receipt_hash72
                                                }
                                            </div>

                                            <div
                                                className="
                                                    mt-1
                                                    text-[10px]
                                                    opacity-40
                                                    font-mono
                                                    break-all
                                                "
                                            >
                                                src:
                                                {" "}
                                                {
                                                    receipt
                                                        .source_hash72
                                                }
                                            </div>

                                        </button>
                                    )
                                }
                            )
                    }

                </div>

            </div>

            {/* ================================================= */}
            {/* Inspector */}
            {/* ================================================= */}

            <div
                className="
                    flex-1
                    overflow-auto
                    bg-black
                    font-mono
                    text-xs
                "
            >

                {
                    selectedReceipt
                        ? (

                            <ReceiptDetailsPanel
                                receipt={
                                    selectedReceipt
                                }
                            />

                        ) : (

                            <EmptyInspectorState />
                        )
                }

            </div>

        </div>
    )
}

// =========================================================
// Receipt Details
// =========================================================

interface ReceiptDetailsPanelProps {

    receipt: RuntimeReceipt
}

const ReceiptDetailsPanel: React.FC<
    ReceiptDetailsPanelProps
> = ({
    receipt
}) => {

    return (

        <div
            className="
                p-6
                flex
                flex-col
                gap-6
            "
        >

            {/* --------------------------------------------- */}
            {/* Title */}
            {/* --------------------------------------------- */}

            <div>

                <div
                    className="
                        text-lg
                        font-semibold
                        text-cyan-400
                        mb-2
                    "
                >
                    Runtime Receipt
                </div>

                <div
                    className="
                        opacity-50
                    "
                >
                    deterministic execution lineage
                </div>

            </div>

            {/* --------------------------------------------- */}
            {/* Metadata */}
            {/* --------------------------------------------- */}

            <div
                className="
                    grid
                    grid-cols-2
                    gap-6
                "
            >

                <InspectorField
                    label="operation"
                    value={
                        receipt.operation
                    }
                />

                <InspectorField
                    label="closure_class"
                    value={
                        receipt
                            .closure_class
                            ?? "stable"
                    }
                />

                <InspectorField
                    label="converged"
                    value={
                        String(
                            receipt
                                .converged
                        )
                    }
                />

                <InspectorField
                    label="halted"
                    value={
                        String(
                            receipt
                                .halted
                        )
                    }
                />

            </div>

            {/* --------------------------------------------- */}
            {/* Receipt Hash */}
            {/* --------------------------------------------- */}

            <div
                className="
                    flex
                    flex-col
                    gap-2
                "
            >

                <div
                    className="
                        text-xs
                        uppercase
                        tracking-wide
                        opacity-50
                    "
                >
                    receipt_hash72
                </div>

                <HashBlock
                    value={
                        receipt
                            .receipt_hash72
                    }
                />

            </div>

            {/* --------------------------------------------- */}
            {/* Source Hash */}
            {/* --------------------------------------------- */}

            <div
                className="
                    flex
                    flex-col
                    gap-2
                "
            >

                <div
                    className="
                        text-xs
                        uppercase
                        tracking-wide
                        opacity-50
                    "
                >
                    source_hash72
                </div>

                <HashBlock
                    value={
                        receipt
                            .source_hash72
                    }
                />

            </div>

            {/* --------------------------------------------- */}
            {/* Chain Visualization */}
            {/* --------------------------------------------- */}

            <div
                className="
                    mt-4
                "
            >

                <div
                    className="
                        text-xs
                        uppercase
                        tracking-wide
                        opacity-50
                        mb-4
                    "
                >
                    receipt_chain_projection
                </div>

                <div
                    className="
                        flex
                        items-center
                        gap-3
                        overflow-auto
                    "
                >

                    {
                        receipt
                            .receipt_hash72
                            .split("")
                            .slice(0, 48)
                            .map(

                                (
                                    char,
                                    index
                                ) => (

                                    <div
                                        key={index}
                                        className="
                                            w-8
                                            h-8
                                            shrink-0
                                            rounded-md
                                            border
                                            border-cyan-500/20
                                            bg-cyan-500/5
                                            flex
                                            items-center
                                            justify-center
                                            text-[10px]
                                            text-cyan-300
                                        "
                                    >
                                        {char}
                                    </div>
                                )
                            )
                    }

                </div>

            </div>

        </div>
    )
}

// =========================================================
// Inspector Field
// =========================================================

interface InspectorFieldProps {

    label: string

    value: string
}

const InspectorField: React.FC<
    InspectorFieldProps
> = ({
    label,
    value
}) => {

    return (

        <div
            className="
                flex
                flex-col
                gap-2
            "
        >

            <div
                className="
                    text-[10px]
                    uppercase
                    tracking-wide
                    opacity-50
                "
            >
                {label}
            </div>

            <div
                className="
                    rounded-lg
                    border
                    border-neutral-800
                    bg-neutral-950
                    px-3
                    py-2
                    break-all
                "
            >
                {value}
            </div>

        </div>
    )
}

// =========================================================
// Hash Block
// =========================================================

interface HashBlockProps {

    value: string
}

const HashBlock: React.FC<
    HashBlockProps
> = ({
    value
}) => {

    return (

        <div
            className="
                rounded-xl
                border
                border-neutral-800
                bg-neutral-950
                p-4
                break-all
                text-cyan-300
                leading-relaxed
                font-mono
                text-xs
            "
        >
            {value}
        </div>
    )
}

// =========================================================
// Empty State
// =========================================================

const EmptyInspectorState: React.FC =
() => {

    return (

        <div
            className="
                w-full
                h-full
                flex
                items-center
                justify-center
                text-neutral-600
                font-mono
                text-sm
            "
        >

            select_receipt_to_inspect

        </div>
    )
}

export default ReceiptInspector