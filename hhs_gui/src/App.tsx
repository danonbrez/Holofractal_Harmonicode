import React from "react"

import {
    RuntimeShell
} from "../runtime_os/core/RuntimeShell"

import {
    RuntimeOS
} from "../runtime_os/core/RuntimeOS"

/**
 * ===================================================
 * Runtime OS Configuration
 * ===================================================
 *
 * IMPORTANT:
 * ---------------------------------------------------
 * Use relative websocket paths.
 *
 * Vite proxy forwards:
 *
 * /ws/*
 *     →
 * localhost:8000
 *
 * This keeps transport authority portable:
 *
 * - local dev
 * - reverse proxies
 * - nginx
 * - docker ingress
 * - cloud edge routing
 */

const runtimeOS = new RuntimeOS({

    runtimeEndpoint:
        "/ws/runtime",

    replayEndpoint:
        "/ws/replay",

    graphEndpoint:
        "/ws/graph",

    transportEndpoint:
        "/ws/transport",

    diagnosticsEnabled: true,

    mobileMode: true
})

/**
 * ===================================================
 * Application Root
 * ===================================================
 */

export default function App() {

    return (

        <RuntimeShell
            runtimeOS={runtimeOS}
        />
    )
}