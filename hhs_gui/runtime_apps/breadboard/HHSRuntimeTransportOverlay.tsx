import React from "react"

// =========================================================
// Types
// =========================================================

export interface HHSRuntimeTransportOverlayProps {

    visible?: boolean
}

// =========================================================
// HHSRuntimeTransportOverlay
// =========================================================

export const HHSRuntimeTransportOverlay: React.FC<
    HHSRuntimeTransportOverlayProps
> = ({
    visible = true
}) => {

    if (!visible) {

        return null
    }

    return (

        <div
            className="
                absolute
                inset-0
                pointer-events-none
                overflow-hidden
            "
        >

            {/* =====================================================
                Glow Layer
            ====================================================== */}

            <div
                className="
                    absolute
                    inset-0
                    opacity-40
                "
            >

                <div
                    className="
                        absolute
                        left-1/2
                        top-1/2
                        -translate-x-1/2
                        -translate-y-1/2
                        w-[500px]
                        h-[500px]
                        rounded-full
                        bg-cyan-500/10
                        blur-3xl
                    "
                />

            </div>

            {/* =====================================================
                Transport Pulse
            ====================================================== */}

            <div
                className="
                    absolute
                    left-1/2
                    top-1/2
                    -translate-x-1/2
                    -translate-y-1/2
                    w-64
                    h-64
                    rounded-full
                    border
                    border-cyan-400/20
                    animate-pulse
                "
            />

            {/* =====================================================
                Overlay Label
            ====================================================== */}

            <div
                className="
                    absolute
                    bottom-4
                    right-4
                    rounded-lg
                    border
                    border-cyan-950
                    bg-black/70
                    px-3
                    py-2
                    text-[10px]
                    font-mono
                    text-cyan-600
                    backdrop-blur-md
                "
            >
                transport_overlay_active
            </div>

        </div>
    )
}

// =========================================================
// Default Export
// =========================================================

export default HHSRuntimeTransportOverlay