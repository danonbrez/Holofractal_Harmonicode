import{j as n}from"./main-BzENKgnW.js";import"./index-w4d0Ryph.js";const o=({className:e})=>n.jsxs("div",{className:`
                w-full
                h-full
                bg-neutral-950
                text-cyan-400
                overflow-hidden
                relative
                ${e!=null?e:""}
                `,children:[n.jsx("div",{className:`
                    absolute
                    inset-0
                    opacity-20
                `,style:{backgroundImage:`
                        linear-gradient(
                            to right,
                            rgba(34,211,238,0.08) 1px,
                            transparent 1px
                        ),
                        linear-gradient(
                            to bottom,
                            rgba(34,211,238,0.08) 1px,
                            transparent 1px
                        )
                    `,backgroundSize:"32px 32px"}}),n.jsxs("div",{className:`
                    absolute
                    top-0
                    left-0
                    right-0
                    z-10
                    border-b
                    border-cyan-950
                    bg-black/70
                    backdrop-blur-md
                    px-4
                    py-3
                    flex
                    items-center
                    justify-between
                `,children:[n.jsxs("div",{className:`
                        flex
                        flex-col
                    `,children:[n.jsx("div",{className:`
                            text-cyan-300
                            font-semibold
                            text-sm
                            tracking-wide
                        `,children:"HHS Runtime Breadboard"}),n.jsx("div",{className:`
                            text-cyan-700
                            text-xs
                            font-mono
                        `,children:"runtime_transport_projection_surface"})]}),n.jsx("div",{className:`
                        text-[10px]
                        font-mono
                        text-cyan-600
                    `,children:"transport-ready"})]}),n.jsx("div",{className:`
                    absolute
                    inset-0
                    pt-20
                    p-6
                    overflow-auto
                `,children:n.jsxs("div",{className:`
                        w-full
                        h-full
                        min-h-[600px]
                        rounded-2xl
                        border
                        border-cyan-950
                        bg-black/40
                        backdrop-blur-sm
                        relative
                        overflow-hidden
                    `,children:[n.jsxs("div",{className:`
                            absolute
                            left-16
                            top-16
                            flex
                            flex-col
                            gap-8
                        `,children:[n.jsx(t,{title:"Runtime",state:"online"}),n.jsx(t,{title:"Replay",state:"pending"}),n.jsx(t,{title:"Graph",state:"pending"})]}),n.jsxs("svg",{className:`
                            absolute
                            inset-0
                            w-full
                            h-full
                            pointer-events-none
                        `,children:[n.jsx("line",{x1:"180",y1:"90",x2:"340",y2:"180",stroke:"rgba(34,211,238,0.4)",strokeWidth:"2"}),n.jsx("line",{x1:"180",y1:"210",x2:"340",y2:"180",stroke:"rgba(34,211,238,0.2)",strokeWidth:"2"})]}),n.jsx("div",{className:`
                            absolute
                            left-1/2
                            top-1/2
                            -translate-x-1/2
                            -translate-y-1/2
                            w-48
                            h-48
                            rounded-full
                            border
                            border-cyan-500/40
                            bg-cyan-500/5
                            flex
                            items-center
                            justify-center
                            backdrop-blur-md
                            shadow-[0_0_60px_rgba(34,211,238,0.15)]
                        `,children:n.jsxs("div",{className:`
                                flex
                                flex-col
                                items-center
                                gap-2
                            `,children:[n.jsx("div",{className:`
                                    text-cyan-300
                                    text-sm
                                    font-semibold
                                `,children:"Runtime Transport"}),n.jsx("div",{className:`
                                    text-cyan-700
                                    text-[10px]
                                    font-mono
                                `,children:"websocket_projection"})]})})]})})]}),t=({title:e,state:r})=>{const s=(()=>{switch(r){case"online":return"bg-emerald-500";case"pending":return"bg-yellow-500";case"offline":return"bg-red-500";default:return"bg-neutral-500"}})();return n.jsxs("div",{className:`
                w-40
                rounded-xl
                border
                border-cyan-950
                bg-black/70
                backdrop-blur-sm
                px-4
                py-3
                flex
                items-center
                justify-between
            `,children:[n.jsx("div",{className:`
                    text-cyan-300
                    text-sm
                    font-medium
                `,children:e}),n.jsx("div",{className:`
                    w-3
                    h-3
                    rounded-full
                    ${s}
                `})]})};export{o as HHSRuntimeBreadboard,o as default};
//# sourceMappingURL=HHSRuntimeBreadboard-BUe2t6UY.js.map
