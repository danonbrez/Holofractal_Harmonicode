import React from "react"

import ReactDOM from "react-dom/client"

import App from "./App"

import "./styles/global.css"

/**
 * ===================================================
 * HHS Runtime OS Bootstrap
 * ===================================================
 */

const rootElement =
    document.getElementById("root")

if (!rootElement) {

    throw new Error(
        `
        HHS Runtime OS bootstrap failed:
        missing root element
        `
    )
}

ReactDOM.createRoot(
    rootElement
).render(

    <React.StrictMode>

        <App />

    </React.StrictMode>
)