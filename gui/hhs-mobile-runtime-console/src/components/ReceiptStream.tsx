/**
 * ReceiptStream.tsx
 * ---------------------------------------------------
 * HHS Runtime Receipt Ledger Projection
 *
 * Purpose:
 * Visual runtime receipt stream + replay surface.
 *
 * This layer is observational only.
 * No runtime authority exists here.
 */

import React, {
    useEffect,
    useMemo,
    useRef,
    useState,
} from 'react';

import {
    ChevronRight,
    Clock3,
    GitBranch,
    Orbit,
    Shield,
} from 'lucide-react';

import { useRuntime } from '../hooks/useRuntime';

/* ============================================================
 * Types
 * ============================================================
 */

export interface ReceiptEntry {
    hash72: string;

    parent?: string;

    timestamp: number;

    runtimeState: string;

    witnesses: string[];

    entropy?: number;

    transportFlux?: number;
}

/* ============================================================
 * Witness Colors
 * ============================================================
 */

const witnessColor = (
    witness: string
): string => {

    if (witness.includes('CONVERGED')) {
        return 'text-green-300 border-green-500/20';
    }

    if (witness.includes('QGU')) {
        return 'text-cyan-300 border-cyan-500/20';
    }

    if (witness.includes('ORBIT')) {
        return 'text-purple-300 border-purple-500/20';
    }

    if (witness.includes('HALT')) {
        return 'text-neutral-300 border-neutral-500/20';
    }

    if (witness.includes('DIVERGENCE')) {
        return 'text-red-300 border-red-500/20';
    }

    return 'text-blue-300 border-blue-500/20';
};

/* ============================================================
 * Component
 * ============================================================
 */

export const ReceiptStream: React.FC = () => {

    const {
        activeReceipt,
        runtimeState,
        telemetry,
    } = useRuntime();

    const [receipts, setReceipts] = useState<
        ReceiptEntry[]
    >([]);

    const containerRef = useRef<
        HTMLDivElement | null
    >(null);

    /* ========================================================
     * Receipt Streaming
     * ======================================================== */

    useEffect(() => {

        if (!activeReceipt) {
            return;
        }

        setReceipts((prev) => {

            const exists = prev.some(
                (r) => r.hash72 === activeReceipt.hash72
            );

            if (exists) {
                return prev;
            }

            const next: ReceiptEntry = {
                hash72: activeReceipt.hash72,

                parent: activeReceipt.parent,

                timestamp: activeReceipt.timestamp,

                runtimeState,

                witnesses: activeReceipt.witnesses,

                entropy: telemetry.entropy,

                transportFlux:
                    telemetry.transportFlux,
            };

            return [
                next,
                ...prev,
            ].slice(0, 64);

        });

    }, [
        activeReceipt,
        runtimeState,
        telemetry,
    ]);

    /* ========================================================
     * Auto Scroll
     * ======================================================== */

    useEffect(() => {

        if (!containerRef.current) {
            return;
        }

        containerRef.current.scrollTop = 0;

    }, [receipts]);

    /* ========================================================
     * Derived Metrics
     * ======================================================== */

    const receiptCount = useMemo(() => {
        return receipts.length;
    }, [receipts]);

    const latestEntropy = useMemo(() => {

        if (!receipts.length) {
            return 0;
        }

        return receipts[0].entropy ?? 0;

    }, [receipts]);

    /* ========================================================
     * Render
     * ======================================================== */

    return (

        <div className="
            fixed
            left-6
            top-6

            w-[420px]
            max-w-[92vw]

            z-[9997]
        ">

            <div className="
                relative
                overflow-hidden

                rounded-2xl

                border
                border-white/10

                bg-black/70
                backdrop-blur-2xl

                shadow-2xl
            ">

                {/* ====================================================
                 * Glow Layer
                 * ==================================================== */}

                <div className="
                    absolute
                    inset-0

                    bg-gradient-to-br
                    from-cyan-500/5
                    via-transparent
                    to-blue-500/5

                    pointer-events-none
                " />

                {/* ====================================================
                 * Header
                 * ==================================================== */}

                <div className="
                    relative

                    flex
                    items-center
                    justify-between

                    px-5
                    py-4

                    border-b
                    border-white/5
                ">

                    <div className="
                        flex
                        items-center
                        gap-3
                    ">

                        <div className="
                            flex
                            items-center
                            justify-center

                            w-10
                            h-10

                            rounded-xl

                            border
                            border-cyan-500/20

                            bg-cyan-500/10
                        ">

                            <Shield
                                size={18}
                                className="
                                    text-cyan-300
                                "
                            />

                        </div>

                        <div>

                            <div className="
                                text-sm
                                font-semibold
                                text-cyan-50
                            ">
                                Receipt Stream
                            </div>

                            <div className="
                                text-[10px]
                                uppercase
                                tracking-[0.3em]

                                text-neutral-500
                                font-mono
                            ">
                                Runtime Ledger
                            </div>

                        </div>

                    </div>

                    <div className="
                        text-right
                    ">

                        <div className="
                            text-sm
                            text-cyan-200
                            font-semibold
                        ">
                            {receiptCount}
                        </div>

                        <div className="
                            text-[10px]
                            uppercase
                            tracking-[0.2em]

                            text-neutral-500
                            font-mono
                        ">
                            Receipts
                        </div>

                    </div>

                </div>

                {/* ====================================================
                 * Runtime Metrics
                 * ==================================================== */}

                <div className="
                    px-5
                    py-4

                    border-b
                    border-white/5

                    grid
                    grid-cols-3
                    gap-4
                ">

                    <div>

                        <div className="
                            text-[10px]
                            uppercase
                            tracking-[0.2em]

                            text-neutral-500
                            font-mono

                            mb-1
                        ">
                            Runtime
                        </div>

                        <div className="
                            text-sm
                            text-cyan-300
                            font-semibold
                        ">
                            {runtimeState}
                        </div>

                    </div>

                    <div>

                        <div className="
                            text-[10px]
                            uppercase
                            tracking-[0.2em]

                            text-neutral-500
                            font-mono

                            mb-1
                        ">
                            Entropy
                        </div>

                        <div className="
                            text-sm
                            text-red-300
                            font-semibold
                        ">
                            {latestEntropy.toFixed(6)}
                        </div>

                    </div>

                    <div>

                        <div className="
                            text-[10px]
                            uppercase
                            tracking-[0.2em]

                            text-neutral-500
                            font-mono

                            mb-1
                        ">
                            Replay
                        </div>

                        <div className="
                            text-sm
                            text-indigo-300
                            font-semibold
                        ">
                            ENABLED
                        </div>

                    </div>

                </div>

                {/* ====================================================
                 * Receipt List
                 * ==================================================== */}

                <div
                    ref={containerRef}
                    className="
                        relative

                        max-h-[640px]
                        overflow-y-auto

                        p-4

                        space-y-4
                    "
                >

                    {receipts.length > 0 ? (

                        receipts.map((receipt) => (

                            <div
                                key={receipt.hash72}
                                className="
                                    relative

                                    rounded-2xl

                                    border
                                    border-white/5

                                    bg-white/[0.02]

                                    overflow-hidden
                                "
                            >

                                {/* ========================================
                                 * Accent
                                 * ======================================== */}

                                <div className="
                                    absolute
                                    left-0
                                    top-0
                                    bottom-0

                                    w-[2px]

                                    bg-gradient-to-b
                                    from-cyan-500
                                    to-blue-500
                                " />

                                {/* ========================================
                                 * Content
                                 * ======================================== */}

                                <div className="
                                    p-4
                                    pl-5
                                ">

                                    {/* Hash */}

                                    <div className="
                                        flex
                                        items-start
                                        justify-between
                                        gap-4
                                    ">

                                        <div className="
                                            flex-1
                                            min-w-0
                                        ">

                                            <div className="
                                                text-[10px]
                                                uppercase
                                                tracking-[0.2em]

                                                text-neutral-500
                                                font-mono

                                                mb-2
                                            ">
                                                Hash72 Receipt
                                            </div>

                                            <div className="
                                                break-all

                                                text-[11px]
                                                font-mono

                                                text-cyan-200
                                            ">
                                                {receipt.hash72}
                                            </div>

                                        </div>

                                        <div className="
                                            flex
                                            items-center
                                            gap-1

                                            text-[10px]
                                            text-neutral-500
                                            font-mono
                                        ">

                                            <Clock3 size={10} />

                                            {new Date(
                                                receipt.timestamp
                                            ).toLocaleTimeString()}

                                        </div>

                                    </div>

                                    {/* Parent */}

                                    {receipt.parent && (

                                        <div className="
                                            mt-4

                                            flex
                                            items-center
                                            gap-2

                                            text-[10px]
                                            font-mono
                                            text-neutral-500
                                        ">

                                            <GitBranch size={10} />

                                            <span>
                                                Parent
                                            </span>

                                            <ChevronRight size={10} />

                                            <span className="
                                                text-blue-300
                                            ">
                                                {receipt.parent.slice(0, 16)}
                                            </span>

                                        </div>

                                    )}

                                    {/* Witnesses */}

                                    <div className="
                                        mt-4

                                        flex
                                        flex-wrap
                                        gap-2
                                    ">

                                        {receipt.witnesses.map(
                                            (witness) => (

                                                <div
                                                    key={witness}
                                                    className={`
                                                        px-2
                                                        py-1

                                                        rounded-lg

                                                        border

                                                        text-[9px]
                                                        font-mono

                                                        ${witnessColor(
                                                            witness
                                                        )}
                                                    `}
                                                >
                                                    {witness}
                                                </div>

                                            )
                                        )}

                                    </div>

                                    {/* Metrics */}

                                    <div className="
                                        mt-4

                                        flex
                                        items-center
                                        justify-between

                                        text-[10px]
                                        font-mono
                                    ">

                                        <div className="
                                            flex
                                            items-center
                                            gap-2

                                            text-purple-300
                                        ">

                                            <Orbit size={10} />

                                            FLUX ::
                                            {' '}
                                            {(
                                                receipt.transportFlux ?? 0
                                            ).toFixed(4)}

                                        </div>

                                        <div className="
                                            text-red-300
                                        ">

                                            Δe ::
                                            {' '}
                                            {(
                                                receipt.entropy ?? 0
                                            ).toFixed(6)}

                                        </div>

                                    </div>

                                </div>

                            </div>

                        ))

                    ) : (

                        <div className="
                            rounded-2xl

                            border
                            border-white/5

                            bg-white/[0.02]

                            p-8

                            text-center
                        ">

                            <div className="
                                text-neutral-600
                                text-sm
                                font-mono
                            ">
                                Awaiting receipt stream...
                            </div>

                        </div>

                    )}

                </div>

            </div>

        </div>

    );

};

export default ReceiptStream;