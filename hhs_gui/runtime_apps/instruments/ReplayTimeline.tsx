import React, {
    useEffect,
    useMemo,
    useState
} from "react"

import {
    RuntimeStateStore,

    RuntimeTimelineFrame

} from "../../runtime_os/state/RuntimeStateStore"

// =========================================================
// Props
// =========================================================

export interface ReplayTimelineProps {

    runtimeStore:
        RuntimeStateStore
}

// =========================================================
// ReplayTimeline
// =========================================================

const ReplayTimeline: React.FC<
    ReplayTimelineProps
> = ({
    runtimeStore
}) => {

    const [timeline, setTimeline] =
        useState<
            RuntimeTimelineFrame[]
        >(

            runtimeStore
                .getTimeline()
        )

    const [selectedFrame, setSelectedFrame] =
        useState<
            RuntimeTimelineFrame
            | null
        >(null)

    const [filter, setFilter] =
        useState("")

    const [autoScroll, setAutoScroll] =
        useState(true)

    // =====================================================
    // Runtime Subscription
    // =====================================================

    useEffect(() => {

        const unsubscribe =
            runtimeStore.subscribe(

                (state) => {

                    setTimeline([
                        ...state.timeline
                    ])
                }
            )

        return () => {

            unsubscribe()
        }

    }, [runtimeStore])

    // =====================================================
    // Filtered Timeline
    // =====================================================

    const filteredTimeline =
        useMemo(() => {

            if (!filter.trim()) {

                return timeline
            }

            const needle =
                filter.toLowerCase()

            return timeline.filter(

                (frame) => (

                    frame
                        .event_type
                        .toLowerCase()
                        .includes(needle)

                    ||

                    JSON.stringify(
                        frame.payload
                    )
                        .toLowerCase()
                        .includes(needle)
                )
            )

        }, [

            timeline,

            filter
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
            {/* Timeline Stream */}
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
                        bg-neutral-900
                        px-4
                        flex
                        items-center
                        justify-between
                    "
                >

                    <div
                        className="
                            text-sm
                            font-semibold
                            tracking-wide
                        "
                    >
                        Replay Timeline
                    </div>

                    <div
                        className="
                            text-xs
                            opacity-60
                            font-mono
                        "
                    >
                        {
                            filteredTimeline
                                .length
                        }
                        {" "}
                        frames
                    </div>

                </div>

                {/* --------------------------------------------- */}
                {/* Controls */}
                {/* --------------------------------------------- */}

                <div
                    className="
                        border-b
                        border-neutral-800
                        p-3
                        flex
                        flex-col
                        gap-3
                        bg-neutral-900/50
                    "
                >

                    <input
                        value={filter}
                        onChange={(e) => {

                            setFilter(
                                e.target.value
                            )
                        }}
                        placeholder="
                            filter event stream
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

                    <label
                        className="
                            flex
                            items-center
                            gap-2
                            text-xs
                            opacity-70
                            select-none
                        "
                    >

                        <input
                            type="checkbox"
                            checked={
                                autoScroll
                            }
                            onChange={(e) => {

                                setAutoScroll(
                                    e.target.checked
                                )
                            }}
                        />

                        auto_scroll

                    </label>

                </div>

                {/* --------------------------------------------- */}
                {/* Timeline Frames */}
                {/* --------------------------------------------- */}

                <div
                    className="
                        flex-1
                        overflow-auto
                    "
                >

                    {
                        filteredTimeline
                            .slice()
                            .reverse()
                            .map(

                                (
                                    frame,
                                    index
                                ) => {

                                    const active =

                                        selectedFrame
                                        === frame

                                    return (

                                        <button
                                            key={index}
                                            onClick={() => {

                                                setSelectedFrame(
                                                    frame
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

                                            {/* ---------------- */}
                                            {/* Header */}
                                            {/* ---------------- */}

                                            <div
                                                className="
                                                    flex
                                                    items-center
                                                    justify-between
                                                    mb-1
                                                "
                                            >

                                                <div
                                                    className={`
                                                        text-xs
                                                        font-semibold
                                                        uppercase
                                                        tracking-wide
                                                        ${
                                                            colorForEvent(
                                                                frame.event_type
                                                            )
                                                        }
                                                    `}
                                                >
                                                    {
                                                        frame.event_type
                                                    }
                                                </div>

                                                <div
                                                    className="
                                                        text-[10px]
                                                        opacity-40
                                                        font-mono
                                                    "
                                                >
                                                    seq:
                                                    {" "}
                                                    {
                                                        frame
                                                            .sequence_id
                                                    }
                                                </div>

                                            </div>

                                            {/* ---------------- */}
                                            {/* Timestamp */}
                                            {/* ---------------- */}

                                            <div
                                                className="
                                                    text-[10px]
                                                    opacity-50
                                                    font-mono
                                                    mb-2
                                                "
                                            >
                                                {
                                                    frame
                                                        .timestamp_ns
                                                }
                                            </div>

                                            {/* ---------------- */}
                                            {/* Preview */}
                                            {/* ---------------- */}

                                            <div
                                                className="
                                                    text-[10px]
                                                    opacity-70
                                                    font-mono
                                                    break-all
                                                "
                                            >
                                                {
                                                    previewPayload(
                                                        frame.payload
                                                    )
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
                    selectedFrame
                        ? (

                            <ReplayFrameInspector
                                frame={
                                    selectedFrame
                                }
                            />

                        ) : (

                            <EmptyReplayState />
                        )
                }

            </div>

        </div>
    )
}

// =========================================================
// Replay Inspector
// =========================================================

interface ReplayFrameInspectorProps {

    frame: RuntimeTimelineFrame
}

const ReplayFrameInspector: React.FC<
    ReplayFrameInspectorProps
> = ({
    frame
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
            {/* Header */}
            {/* --------------------------------------------- */}

            <div>

                <div
                    className={`
                        text-lg
                        font-semibold
                        uppercase
                        tracking-wide
                        ${colorForEvent(
                            frame.event_type
                        )}
                    `}
                >
                    {
                        frame.event_type
                    }
                </div>

                <div
                    className="
                        opacity-50
                        mt-2
                    "
                >
                    deterministic replay frame
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

                <ReplayField
                    label="sequence_id"
                    value={
                        String(
                            frame
                                .sequence_id
                        )
                    }
                />

                <ReplayField
                    label="timestamp_ns"
                    value={
                        String(
                            frame
                                .timestamp_ns
                        )
                    }
                />

                <ReplayField
                    label="event_type"
                    value={
                        frame
                            .event_type
                    }
                />

            </div>

            {/* --------------------------------------------- */}
            {/* Payload */}
            {/* --------------------------------------------- */}

            <div>

                <div
                    className="
                        text-xs
                        uppercase
                        tracking-wide
                        opacity-50
                        mb-3
                    "
                >
                    payload
                </div>

                <pre
                    className="
                        rounded-xl
                        border
                        border-neutral-800
                        bg-neutral-950
                        p-4
                        overflow-auto
                        text-[11px]
                        leading-relaxed
                        text-cyan-300
                    "
                >
                    {
                        JSON.stringify(
                            frame.payload,
                            null,
                            2
                        )
                    }
                </pre>

            </div>

            {/* --------------------------------------------- */}
            {/* Event Projection */}
            {/* --------------------------------------------- */}

            <div>

                <div
                    className="
                        text-xs
                        uppercase
                        tracking-wide
                        opacity-50
                        mb-4
                    "
                >
                    event_projection
                </div>

                <div
                    className="
                        flex
                        flex-wrap
                        gap-2
                    "
                >

                    {
                        Object.keys(
                            frame.payload
                        ).map(

                            (
                                key
                            ) => (

                                <div
                                    key={key}
                                    className="
                                        rounded-md
                                        border
                                        border-cyan-500/20
                                        bg-cyan-500/5
                                        px-3
                                        py-2
                                        text-[10px]
                                        text-cyan-300
                                    "
                                >
                                    {key}
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
// Replay Field
// =========================================================

interface ReplayFieldProps {

    label: string

    value: string
}

const ReplayField: React.FC<
    ReplayFieldProps
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
// Empty State
// =========================================================

const EmptyReplayState: React.FC =
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

            select_replay_frame

        </div>
    )
}

// =========================================================
// Helpers
// =========================================================

function previewPayload(
    payload: Record<
        string,
        unknown
    >
): string {

    try {

        return JSON.stringify(
            payload
        ).slice(0, 120)

    } catch {

        return "[payload]"
    }
}

// ---------------------------------------------------------

function colorForEvent(
    eventType: string
): string {

    switch (eventType) {

        case "runtime":

            return "text-cyan-400"

        case "replay":

            return "text-green-400"

        case "graph":

            return "text-purple-400"

        case "transport":

            return "text-orange-400"

        case "receipt":

            return "text-pink-400"

        case "certification":

            return "text-yellow-400"

        default:

            return "text-neutral-400"
    }
}

export default ReplayTimeline