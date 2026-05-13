/**
 * HHS Intent Bar (Stage 1 Ingress)
 * ---------------------------------------------------
 * Sovereign Runtime Command Interface
 *
 * Design Goals:
 * - Deterministic ingress only
 * - No frontend execution authority
 * - Runtime-driven telemetry
 * - Aerospace translucent console aesthetic
 * - Kernel-first topology
 */

import React, {
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
} from 'react';

import {
    Activity,
    AlertTriangle,
    Orbit,
    Send,
    Shield,
    Sparkles,
} from 'lucide-react';

import { useRuntime } from '../hooks/useRuntime';

/* ============================================================
 * Runtime Types
 * ============================================================
 */

export type RuntimeState =
    | 'IDLE'
    | 'ROUTING'
    | 'EXECUTING'
    | 'CLOSURE'
    | 'REJOIN'
    | 'DIVERGENCE'
    | 'ORBIT'
    | 'HALT';

export interface HHSIntentIngress {
    id: string;
    timestamp: number;

    modality: 'text';

    payload: string;

    origin:
        | 'intent_bar'
        | 'voice_ingress'
        | 'vm_terminal'
        | 'api'
        | 'replay_engine';

    requested_mode?:
        | 'symbolic'
        | 'runtime'
        | 'trace'
        | 'receipt'
        | 'graph'
        | 'adaptive';

    parent_receipt?: string;
}

/* ============================================================
 * Runtime State Styling
 * ============================================================
 */

const RUNTIME_STYLES: Record<
    RuntimeState,
    {
        border: string;
        glow: string;
        text: string;
        icon: React.ReactNode;
        label: string;
    }
> = {
    IDLE: {
        border: 'border-cyan-500/20',
        glow: 'from-cyan-500 to-blue-500',
        text: 'text-cyan-300',
        icon: <Activity size={12} />,
        label: 'Idle',
    },

    ROUTING: {
        border: 'border-yellow-500/30',
        glow: 'from-yellow-500 to-orange-500',
        text: 'text-yellow-300',
        icon: <Sparkles size={12} />,
        label: 'Routing',
    },

    EXECUTING: {
        border: 'border-blue-500/30',
        glow: 'from-blue-500 to-cyan-500',
        text: 'text-blue-300',
        icon: <Activity size={12} className="animate-pulse" />,
        label: 'Executing',
    },

    CLOSURE: {
        border: 'border-emerald-500/30',
        glow: 'from-emerald-500 to-green-500',
        text: 'text-emerald-300',
        icon: <Shield size={12} />,
        label: 'Closure',
    },

    REJOIN: {
        border: 'border-indigo-500/30',
        glow: 'from-indigo-500 to-blue-500',
        text: 'text-indigo-300',
        icon: <Sparkles size={12} />,
        label: 'Rejoin',
    },

    DIVERGENCE: {
        border: 'border-red-500/40',
        glow: 'from-red-500 to-orange-500',
        text: 'text-red-300',
        icon: <AlertTriangle size={12} />,
        label: 'Divergence',
    },

    ORBIT: {
        border: 'border-purple-500/40',
        glow: 'from-purple-500 to-fuchsia-500',
        text: 'text-purple-300',
        icon: <Orbit size={12} />,
        label: 'Orbit',
    },

    HALT: {
        border: 'border-neutral-500/30',
        glow: 'from-neutral-500 to-neutral-700',
        text: 'text-neutral-300',
        icon: <Shield size={12} />,
        label: 'Halt',
    },
};

/* ============================================================
 * Helpers
 * ============================================================
 */

function createIngressPacket(
    payload: string,
    parentReceipt?: string
): HHSIntentIngress {
    return {
        id: crypto.randomUUID(),
        timestamp: Date.now(),

        modality: 'text',

        payload,

        origin: 'intent_bar',

        requested_mode: inferRequestedMode(payload),

        parent_receipt: parentReceipt,
    };
}

function inferRequestedMode(
    payload: string
): HHSIntentIngress['requested_mode'] {
    const p = payload.trim().toLowerCase();

    if (
        p.includes('trace') ||
        p.includes('receipt')
    ) {
        return 'trace';
    }

    if (
        p.includes('graph') ||
        p.includes('tensor')
    ) {
        return 'graph';
    }

    if (
        p.includes('adaptive') ||
        p.includes('learn')
    ) {
        return 'adaptive';
    }

    if (
        p.includes('Δe') ||
        p.includes('Ψ') ||
        p.includes('Θ') ||
        p.includes('Ω') ||
        p.includes('xy') ||
        p.includes('=')
    ) {
        return 'symbolic';
    }

    return 'runtime';
}

/* ============================================================
 * Intent Bar
 * ============================================================
 */

export const IntentBar: React.FC = () => {
    const [intent, setIntent] = useState('');
    const [focused, setFocused] = useState(false);

    const inputRef = useRef<HTMLInputElement | null>(null);

    const {
        router,

        runtimeState = 'IDLE',

        activeReceipt,
        telemetry,
        witnesses,
    } = useRuntime();

    const style = useMemo(
        () => RUNTIME_STYLES[runtimeState],
        [runtimeState]
    );

    const handleSubmit = useCallback(
        async (e: React.FormEvent) => {
            e.preventDefault();

            const trimmed = intent.trim();

            if (!trimmed) return;

            const packet = createIngressPacket(
                trimmed,
                activeReceipt?.hash72
            );

            try {
                await router.routeIntent(packet);
                setIntent('');
            } catch (err) {
                console.error('[HHS::Ingress]', err);
            }
        },
        [intent, router, activeReceipt]
    );

    useEffect(() => {
        const handler = (e: KeyboardEvent) => {
            if (
                e.key === '/' &&
                document.activeElement !== inputRef.current
            ) {
                e.preventDefault();
                inputRef.current?.focus();
            }
        };

        window.addEventListener('keydown', handler);

        return () => {
            window.removeEventListener('keydown', handler);
        };
    }, []);

    return (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 w-[720px] max-w-[92vw] z-[9999]">

            {/* ====================================================
             * Telemetry Shell
             * ==================================================== */}

            <div
                className={`
                    relative
                    rounded-2xl
                    border
                    ${style.border}
                    bg-black/70
                    backdrop-blur-2xl
                    shadow-2xl
                    overflow-hidden
                    transition-all
                    duration-500
                `}
            >

                {/* Glow Layer */}

                <div
                    className={`
                        absolute
                        -inset-[1px]
                        rounded-2xl
                        bg-gradient-to-r
                        ${style.glow}
                        opacity-20
                        blur-xl
                        transition-all
                        duration-700
                        ${focused ? 'opacity-40' : 'opacity-20'}
                    `}
                />

                {/* Grid Overlay */}

                <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[linear-gradient(to_right,#ffffff_1px,transparent_1px),linear-gradient(to_bottom,#ffffff_1px,transparent_1px)] bg-[size:24px_24px]" />

                {/* ====================================================
                 * Top Telemetry Bar
                 * ==================================================== */}

                <div className="relative flex items-center justify-between px-4 py-2 border-b border-white/5">

                    <div className="flex items-center gap-2 text-[11px] font-mono tracking-wider uppercase">

                        <div className={style.text}>
                            {style.icon}
                        </div>

                        <span className={style.text}>
                            {style.label}
                        </span>

                    </div>

                    <div className="flex items-center gap-4 text-[10px] font-mono text-neutral-500">

                        <div>
                            INGRESS :: STAGE_1
                        </div>

                        {telemetry?.transportFlux !== undefined && (
                            <div>
                                FLUX :: {telemetry.transportFlux.toFixed(4)}
                            </div>
                        )}

                        {witnesses?.length > 0 && (
                            <div className="text-cyan-400">
                                {witnesses[0]}
                            </div>
                        )}

                    </div>

                </div>

                {/* ====================================================
                 * Input Form
                 * ==================================================== */}

                <form
                    onSubmit={handleSubmit}
                    className="relative"
                >

                    <input
                        ref={inputRef}
                        type="text"
                        value={intent}
                        spellCheck={false}
                        autoComplete="off"

                        onFocus={() => setFocused(true)}
                        onBlur={() => setFocused(false)}

                        onChange={(e) => {
                            setIntent(e.target.value);
                        }}

                        placeholder="Enter Intent or Symbolic Algebra (Δe, Ψ, Θ, Ω, xy...)"

                        className="
                            relative
                            w-full
                            bg-transparent
                            text-cyan-50
                            px-6
                            py-5
                            pr-32
                            font-mono
                            text-sm
                            tracking-wide
                            focus:outline-none
                            placeholder:text-neutral-500
                        "
                    />

                    {/* ====================================================
                     * Kernel Label
                     * ==================================================== */}

                    <div className="absolute right-20 top-1/2 -translate-y-1/2 text-[10px] font-mono tracking-[0.25em] uppercase text-neutral-500 pointer-events-none">

                        Kernel Ingress

                    </div>

                    {/* ====================================================
                     * Submit Button
                     * ==================================================== */}

                    <button
                        type="submit"
                        disabled={!intent.trim()}
                        className="
                            absolute
                            right-3
                            top-1/2
                            -translate-y-1/2

                            flex
                            items-center
                            justify-center

                            w-11
                            h-11

                            rounded-xl

                            border
                            border-cyan-500/20

                            bg-cyan-500/10
                            hover:bg-cyan-500/20

                            text-cyan-300
                            hover:text-cyan-100

                            transition-all
                            duration-300

                            disabled:opacity-30
                            disabled:cursor-not-allowed
                        "
                    >
                        <Send size={16} />
                    </button>

                </form>

                {/* ====================================================
                 * Footer Status
                 * ==================================================== */}

                <div className="relative flex items-center justify-between px-4 py-2 border-t border-white/5 text-[10px] font-mono">

                    <div className="flex items-center gap-3 text-neutral-500">

                        <span>
                            MODE ::
                            {' '}
                            {runtimeState}
                        </span>

                        {activeReceipt?.hash72 && (
                            <span className="text-cyan-500">
                                RECEIPT ::
                                {' '}
                                {activeReceipt.hash72.slice(0, 18)}
                            </span>
                        )}

                    </div>

                    <div className="text-neutral-600">
                        HHS Runtime Interface
                    </div>

                </div>

            </div>

        </div>
    );
};

export default IntentBar;