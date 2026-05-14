import type {
    Config
} from "tailwindcss"

/**
 * ===================================================
 * HHS Runtime OS Tailwind Configuration
 * ===================================================
 */

export default {

    content: [

        "./index.html",

        "./src/**/*.{ts,tsx}",

        "./runtime_os/**/*.{ts,tsx}",

        "./runtime_apps/**/*.{ts,tsx}"
    ],

    theme: {

        extend: {

            colors: {

                runtime: {

                    background:
                        "#05070b",

                    surface:
                        "#0f1218",

                    panel:
                        "#131720",

                    border:
                        "rgba(255,255,255,0.08)",

                    cyan:
                        "#22d3ee",

                    purple:
                        "#a855f7"
                }
            },

            boxShadow: {

                runtime:
                    `
                    0 20px 80px
                    rgba(0,0,0,0.55)
                    `,

                glow:
                    `
                    0 0 40px
                    rgba(34,211,238,0.18)
                    `
            },

            backdropBlur: {

                runtime: "20px"
            },

            borderRadius: {

                runtime: "18px"
            },

            keyframes: {

                runtimePulse: {

                    "0%": {

                        opacity: "0.35"
                    },

                    "50%": {

                        opacity: "1"
                    },

                    "100%": {

                        opacity: "0.35"
                    }
                },

                runtimeFloat: {

                    "0%": {

                        transform:
                            "translateY(0px)"
                    },

                    "50%": {

                        transform:
                            "translateY(-4px)"
                    },

                    "100%": {

                        transform:
                            "translateY(0px)"
                    }
                },

                runtimeFadeIn: {

                    "0%": {

                        opacity: "0",

                        transform:
                            "translateY(8px)"
                    },

                    "100%": {

                        opacity: "1",

                        transform:
                            "translateY(0px)"
                    }
                }
            },

            animation: {

                runtimePulse:
                    "runtimePulse 2s infinite",

                runtimeFloat:
                    "runtimeFloat 4s ease-in-out infinite",

                runtimeFadeIn:
                    "runtimeFadeIn 280ms ease-out"
            }
        }
    },

    plugins: []
} satisfies Config