/**
 * RuntimeTelemetry.tsx
 * ---------------------------------------------------
 * HHS Runtime Observability Surface
 *
 * Purpose:
 * Live runtime telemetry projection layer.
 *
 * This component is observational only.
 * No execution authority exists here.
 */

import React, { useMemo } from 'react';

import {
    Activity,
    AlertTriangle,
    CheckCircle2,
    Orbit,
    Shield,
    Wifi,
    WifiOff,
} from 'lucide-react';

import { useRuntime } from '../hooks/useRuntime';

/* ============================================================
 * Witness Styling
 * ============================================================
 */

const WITNESS_STYLES: Record<
    string,
    string
> = {
    W_QGU_APPLIED:
        'border-cyan-500/30 text-cyan-300 bg-cyan-500/10',

    W_CLOSE_TRANSPORT:
        'border-blue-500/30 text-blue-300 bg-blue-500/10',

    W_CLOSE_CONSTRAINT:
        'border-emerald-500/30 text-emerald-300 bg-emerald-500/10',

    W_CLOSE_ORIENTATION:
        'border-indigo-500/30 text-indigo-300 bg-indigo-500/10',

    W_CONVERGED:
        'border-green-500/40 text-green-300 bg-green-500/10',

    W_ORBIT_DETECTED:
        'border-purple-500/40 text-purple-300 bg-purple-500/10',

    W_HALT:
        'border-neutral-500/30 text-neutral-300 bg-neutral-500/10',
};

/* ============================================================
 * Helpers
 * ============================================================
 */

function fluxColor(
    value: number
): string {

    if (value < 0.25) {
        return 'bg-cyan-500';
    }

    if (value < 0.5) {
        return 'bg-yellow-500';
    }

    if (value < 0.75) {
        return 'bg-orange-500';
    }

    return 'bg-red-500';
}

/* ============================================================
 * Component
 * ============================================================
 */

export const RuntimeTelemetry: React.FC = () => {

    const {
        runtimeState,

        telemetry,

        witnesses,

        connected,

        activeReceipt,
    } = useRuntime();

    const entropyPercent = useMemo(() => {
        return Math.min(
            telemetry.entropy * 100,
            100
        );
    }, [telemetry.entropy]);

    return (

        <div className="fixed top-6 right-6 w-[360px] max-w-[92vw] z-[9998]">

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

                            bg-cyan-500/10
                            border
                            border-cyan-500/20
                        ">

                            <Activity
                                size={18}
                                className="text-cyan-300"
                            />

                        </div>

                        <div>

                            <div className="
                                text-sm
                                font-semibold
                                text-cyan-50
                            ">
                                Runtime Telemetry
                            </div>

                            <div className="
                                text-[10px]
                                uppercase
                                tracking-[0.3em]
                                text-neutral-500
                                font-mono
                            ">
                                Observability Surface
                            </div>

                        </div>

                    </div>

                    <div>

                        {connected ? (
                            <div className="
                                flex
                                items-center
                                gap-2

                                text-emerald-300
                                text-xs
                                font-mono
                            ">
                                <Wifi size={14} />
                                LINKED
                            </div>
                        ) : (
                            <div className="
                                flex
                                items-center
                                gap-2

                                text-red-300
                                text-xs
                                font-mono
                            ">
                                <WifiOff size={14} />
                                OFFLINE
                            </div>
                        )}

                    </div>

                </div>

                {/* ====================================================
                 * Runtime State
                 * ==================================================== */}

                <div className="
                    px-5
                    py-4
                    border-b
                    border-white/5
                ">

                    <div className="
                        flex
                        items-center
                        justify-between
                    ">

                        <div className="
                            text-[11px]
                            uppercase
                            tracking-[0.25em]
                            text-neutral-500
                            font-mono
                        ">
                            Runtime State
                        </div>

                        <div className="
                            text-sm
                            font-semibold
                            text-cyan-200
                        ">
                            {runtimeState}
                        </div>

                    </div>

                </div>

                {/* ====================================================
                 * Flux Metrics
                 * ==================================================== */}

                <div className="
                    px-5
                    py-5
                    border-b
                    border-white/5
                    space-y-5
                ">

                    {/* Transport Flux */}

                    <div>

                        <div className="
                            flex
                            items-center
                            justify-between

                            text-xs
                            font-mono
                            mb-2
                        ">

                            <span className="text-neutral-400">
                                Transport Flux
                            </span>

                            <span className="text-cyan-300">
                                {telemetry.transportFlux.toFixed(4)}
                            </span>

                        </div>

                        <div className="
                            w-full
                            h-2
                            rounded-full
                            bg-white/5
                            overflow-hidden
                        ">

                            <div
                                className={`
                                    h-full
                                    ${fluxColor(
                                        telemetry.transportFlux
                                    )}
                                    transition-all
                                    duration-500
                                `}
                                style={{
                                    width: `${
                                        telemetry.transportFlux * 100
                                    }%`,
                                }}
                            />

                        </div>

                    </div>

                    {/* Constraint Flux */}

                    <div>

                        <div className="
                            flex
                            items-center
                            justify-between

                            text-xs
                            font-mono
                            mb-2
                        ">

                            <span className="text-neutral-400">
                                Constraint Flux
                            </span>

                            <span className="text-emerald-300">
                                {telemetry.constraintFlux.toFixed(4)}
                            </span>

                        </div>

                        <div className="
                            w-full
                            h-2
                            rounded-full
                            bg-white/5
                            overflow-hidden
                        ">

                            <div
                                className="
                                    h-full
                                    bg-emerald-500
                                    transition-all
                                    duration-500
                                "
                                style={{
                                    width: `${
                                        telemetry.constraintFlux * 100
                                    }%`,
                                }}
                            />

                        </div>

                    </div>

                    {/* Entropy */}

                    <div>

                        <div className="
                            flex
                            items-center
                            justify-between

                            text-xs
                            font-mono
                            mb-2
                        ">

                            <span className="text-neutral-400">
                                Entropy
                            </span>

                            <span className="text-red-300">
                                {telemetry.entropy.toFixed(6)}
                            </span>

                        </div>

                        <div className="
                            w-full
                            h-2
                            rounded-full
                            bg-white/5
                            overflow-hidden
                        ">

                            <div
                                className="
                                    h-full
                                    bg-red-500
                                    transition-all
                                    duration-500
                                "
                                style={{
                                    width: `${entropyPercent}%`,
                                }}
                            />

                        </div>

                    </div>

                </div>

                {/* ====================================================
                 * Witness Flags
                 * ==================================================== */}

                <div className="
                    px-5
                    py-5
                    border-b
                    border-white/5
                ">

                    <div className="
                        text-[11px]
                        uppercase
                        tracking-[0.25em]
                        text-neutral-500
                        font-mono
                        mb-4
                    ">
                        Witness Flags
                    </div>

                    <div className="
                        flex
                        flex-wrap
                        gap-2
                    ">

                        {witnesses.length > 0 ? (
                            witnesses.map((witness) => (

                                <div
                                    key={witness}
                                    className={`
                                        px-3
                                        py-2

                                        rounded-lg

                                        border

                                        text-[10px]
                                        font-mono

                                        ${WITNESS_STYLES[witness]
                                            ?? 'border-white/10 text-white'}
                                    `}
                                >
                                    {witness}
                                </div>

                            ))
                        ) : (
                            <div className="
                                text-xs
                                text-neutral-600
                                font-mono
                            ">
                                No active witnesses.
                            </div>
                        )}

                    </div>

                </div>

                {/* ====================================================
                 * Receipt Section
                 * ==================================================== */}

                <div className="
                    px-5
                    py-5
                ">

                    <div className="
                        flex
                        items-center
                        justify-between
                        mb-4
                    ">

                        <div className="
                            text-[11px]
                            uppercase
                            tracking-[0.25em]
                            text-neutral-500
                            font-mono
                        ">
                            Active Receipt
                        </div>

                        <div className="
                            text-cyan-400
                        ">
                            <Shield size={14} />
                        </div>

                    </div>

                    {activeReceipt ? (

                        <div className="
                            rounded-xl
                            border
                            border-cyan-500/10
                            bg-cyan-500/5

                            p-4
                        ">

                            <div className="
                                text-[11px]
                                break-all
                                font-mono
                                text-cyan-200
                            ">
                                {activeReceipt.hash72}
                            </div>

                            <div className="
                                flex
                                items-center
                                gap-3

                                mt-4

                                text-[10px]
                                font-mono
                                text-neutral-500
                            ">

                                <div className="
                                    flex
                                    items-center
                                    gap-1
                                ">
                                    <CheckCircle2 size={10} />
                                    VERIFIED
                                </div>

                                <div className="
                                    flex
                                    items-center
                                    gap-1
                                ">
                                    <Orbit size={10} />
                                    LEDGER LINKED
                                </div>

                            </div>

                        </div>

                    ) : (

                        <div className="
                            rounded-xl
                            border
                            border-white/5
                            bg-white/[0.02]

                            p-4

                            text-xs
                            text-neutral-600
                            font-mono
                        ">
                            Awaiting receipt stream...
                        </div>

                    )}

                </div>

            </div>

        </div>

    );

};

export default RuntimeTelemetry;