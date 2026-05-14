import {
    defineConfig
} from "vite"

import react from
    "@vitejs/plugin-react"

import path from "path"

export default defineConfig({

    plugins: [
        react()
    ],

    resolve: {

        alias: {

            "@":
                path.resolve(
                    __dirname,
                    "./src"
                ),

            "@runtime":
                path.resolve(
                    __dirname,
                    "./runtime_os"
                ),

            "@apps":
                path.resolve(
                    __dirname,
                    "./runtime_apps"
                ),

            "@styles":
                path.resolve(
                    __dirname,
                    "./src/styles"
                )
        }
    },

    server: {

        host: true,

        port: 5173,

        strictPort: true,

        proxy: {

            /**
             * ------------------------------------------------
             * REST API
             * ------------------------------------------------
             */

            "/api": {

                target:
                    "http://localhost:8000",

                changeOrigin: true,

                secure: false
            },

            /**
             * ------------------------------------------------
             * Unified WebSocket Proxy
             * ------------------------------------------------
             */

            "/ws": {

                target:
                    "ws://localhost:8000",

                ws: true,

                changeOrigin: true,

                secure: false
            }
        }
    },

    build: {

        target: "esnext",

        sourcemap: true,

        outDir: "dist",

        emptyOutDir: true
    },

    optimizeDeps: {

        include: [

            "react",

            "react-dom",

            "@react-three/fiber",

            "@react-three/drei",

            "three"
        ]
    }
})