import {
    defineConfig
} from "vite"

import react from "@vitejs/plugin-react"

// =========================================================
// HHS Runtime Vite Config
// =========================================================
//
// IMPORTANT
// ---------------------------------------------------------
// Runtime applications may be:
//
//   - optional
//   - experimental
//   - dynamically discovered
//
// DO NOT aggressively pre-bundle
// runtime application surfaces.
//
// Runtime authority belongs to:
//
//   backend runtime
//   websocket runtime transport
//   runtime_event_schema.py
//
// =========================================================

export default defineConfig({

    plugins: [

        react()
    ],

    // =====================================================
    // Dev Server
    // =====================================================

    server: {

        host: "0.0.0.0",

        port: 5173,

        strictPort: false,

        cors: true,

        proxy: {

            // -------------------------------------------------
            // Runtime API
            // -------------------------------------------------

            "/api": {

                target:
                    "http://127.0.0.1:8000",

                changeOrigin: true,

                secure: false
            },

            // -------------------------------------------------
            // Runtime WS
            // -------------------------------------------------

            "/ws": {

                target:
                    "ws://127.0.0.1:8000",

                ws: true,

                changeOrigin: true,

                secure: false
            }
        }
    },

    // =====================================================
    // Preview
    // =====================================================

    preview: {

        host: "0.0.0.0",

        port: 4173
    },

    // =====================================================
    // OptimizeDeps
    // =====================================================

    optimizeDeps: {

        // -------------------------------------------------
        // IMPORTANT
        // -------------------------------------------------
        //
        // Prevent Vite from attempting
        // aggressive static optimization
        // against optional runtime apps.
        //
        // Dynamic imports use:
        //
        //     /* @vite-ignore */
        //
        // but optimizeDeps can still
        // attempt partial graph resolution.
        //
        // -------------------------------------------------

        exclude: [

            // Breadboard
            "../../runtime_apps/breadboard/HHSRuntimeBreadboard",
            "../../runtime_apps/breadboard/HHSRuntimeTransportOverlay",

            // Calculator
            "../../runtime_apps/calculator/HHSCalculatorSurface",
            "../../runtime_apps/calculator/HHSCalculatorGraphProjection",

            // Instruments
            "../../runtime_apps/instruments/ReceiptInspector",
            "../../runtime_apps/instruments/ReplayTimeline"
        ]
    },

    // =====================================================
    // Build
    // =====================================================

    build: {

        target: "esnext",

        sourcemap: true,

        chunkSizeWarningLimit: 2000,

        rollupOptions: {

            output: {

                manualChunks: {

                    react: [

                        "react",

                        "react-dom"
                    ]
                }
            }
        }
    },

    // =====================================================
    // Resolve
    // =====================================================

    resolve: {

        extensions: [

            ".tsx",

            ".ts",

            ".jsx",

            ".js",

            ".json"
        ]
    },

    // =====================================================
    // Define
    // =====================================================

    define: {

        __HHS_RUNTIME__: true
    }
})