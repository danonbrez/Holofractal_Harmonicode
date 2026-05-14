import React from "react"

import {
    RuntimeShell
} from "../runtime_os/core/RuntimeShell"

import {
    RuntimeOS
} from "../runtime_os/core/RuntimeOS"

const runtimeOS = new RuntimeOS()

export default function App() {

    return (
        <RuntimeShell
            runtimeOS={runtimeOS}
        />
    )
}