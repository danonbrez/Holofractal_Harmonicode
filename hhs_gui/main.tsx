import React from "react"
import ReactDOM from "react-dom/client"

import { RuntimeShell } from "./runtime_os/core/RuntimeShell"
import { RuntimeOS } from "./runtime_os/core/RuntimeOS"

import "./src/styles/global.css"

const runtimeOS = new RuntimeOS({
    runtimeEndpoint: "/ws/runtime",
    replayEndpoint: "/ws/replay",
    graphEndpoint: "/ws/graph",
    transportEndpoint: "/ws/transport",
    diagnosticsEnabled: true,
    mobileMode: window.matchMedia("(max-width: 900px)").matches
})

const rootElement = document.getElementById("root")

if (!rootElement) {
    throw new Error("Missing root element")
}

const root = ReactDOM.createRoot(rootElement)

root.render(
    <React.StrictMode>
        <RuntimeShell runtimeOS={runtimeOS} />
    </React.StrictMode>
)

;(window as typeof window & {
    __HHS_RUNTIME_OS__?: RuntimeOS
}).__HHS_RUNTIME_OS__ = runtimeOS

if (import.meta.hot) {
    import.meta.hot.dispose(() => {
        runtimeOS.destroy()
    })
}
