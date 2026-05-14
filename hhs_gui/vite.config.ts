import {
    defineConfig
} from "vite"

import react from
    "@vitejs/plugin-react"

import path from "path"

/**
 * ===================================================
 * HHS Runtime OS Vite Configuration
 * ===================================================
 */

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

        /**
         * --------------------------------------------
         * Runtime API Proxy
         * --------------------------------------------
         */

        proxy: {

            /**
             * ----------------------------------------
             * REST Runtime API
             * ----------------------------------------
             */

            "/api": {

                target:
                    "http://localhost:8000",

                changeOrigin: true,

                secure: false
            },

            /**
             * ----------------------------------------
             * Runtime Stream
             * ----------------------------------------
             */

            "/ws/runtime": {

                target:
                    "ws://localhost:8000",

                ws: true,

                changeOrigin: true
            },

            /**
             * ----------------------------------------
             * Replay Stream
             * ----------------------------------------
             */

            "/ws/replay": {

                target:
                    "ws://localhost:8000",

                ws: true,

                changeOrigin: true
            },

            /**
             * ----------------------------------------
             * Graph Stream
             * ----------------------------------------
             */

            "/ws/graph": {

                target:
                    "ws://localhost:8000",

                ws: true,

                changeOrigin: true
            },

            /**
             * ----------------------------------------
             * Transport Stream
             * ----------------------------------------
             */

            "/ws/transport": {

                target:
                    "ws://localhost:8000",

                ws: true,

                changeOrigin: true
            }
        }
    },

    /**
     * ---------------------------------------------------
     * Build
     * ---------------------------------------------------
     */

    build: {

        target: "esnext",

        sourcemap: true,

        outDir: "dist",

        emptyOutDir: true
    },

    /**
     * ---------------------------------------------------
     * Optimize
     * ---------------------------------------------------
     */

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