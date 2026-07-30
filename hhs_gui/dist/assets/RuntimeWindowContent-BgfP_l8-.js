const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["assets/HHSCalculatorSurface-IwvAVMsl.js","assets/main-DPcMUe0W.js","assets/index-C0QsYSm-.js","assets/main-DCjgnH6X.css","assets/HHSCalculatorGraphProjection-BIeCki1M.js","assets/HHSRuntimeBreadboard-BypSCblH.js","assets/HHSRuntimeTransportOverlay-Bux0_f_F.js"])))=>i.map(i=>d[i]);
import{_ as l}from"./index-C0QsYSm-.js";import{j as n,r as c,R as s}from"./main-DPcMUe0W.js";async function a(e,r){try{return await e()}catch(t){return console.error("[RuntimeWindowContent] optional runtime surface missing",t),{default:r}}}const d=s.lazy(()=>a(()=>l(()=>import("./HHSCalculatorSurface-IwvAVMsl.js"),__vite__mapDeps([0,1,2,3])),v)),x=s.lazy(()=>a(()=>l(()=>import("./HHSCalculatorGraphProjection-BIeCki1M.js"),__vite__mapDeps([4,1,2,3])),g)),f=s.lazy(()=>a(()=>l(()=>import("./HHSRuntimeBreadboard-BypSCblH.js"),__vite__mapDeps([5,1,2,3])),_)),m=s.lazy(()=>a(()=>l(()=>import("./HHSRuntimeTransportOverlay-Bux0_f_F.js"),__vite__mapDeps([6,1,2,3])),w)),R=({runtimeOS:e,applicationId:r})=>r==="runtime_console"?n.jsx(p,{runtimeOS:e}):r==="calculator"?n.jsx(c.Suspense,{fallback:n.jsx(i,{label:"calculator"}),children:n.jsxs("div",{className:`
                        w-full
                        h-full
                        grid
                        grid-cols-2
                        overflow-hidden
                    `,children:[n.jsx("div",{className:`
                            border-r
                            border-neutral-800
                            overflow-hidden
                        `,children:n.jsx(d,{})}),n.jsx("div",{className:`
                            overflow-hidden
                        `,children:n.jsx(x,{})})]})}):r==="breadboard"?n.jsx(c.Suspense,{fallback:n.jsx(i,{label:"breadboard"}),children:n.jsxs("div",{className:`
                        relative
                        w-full
                        h-full
                        overflow-hidden
                    `,children:[n.jsx(f,{}),n.jsx(m,{})]})}):r==="graph_debugger"?n.jsx(b,{runtimeOS:e}):r==="tensor_inspector"?n.jsx(h,{runtimeOS:e}):r==="replay_viewer"?n.jsx(j,{runtimeOS:e}):n.jsx(y,{applicationId:r}),p=({runtimeOS:e})=>{const r=e.getMetrics();return n.jsxs("div",{className:`
                w-full
                h-full
                bg-black
                text-cyan-400
                font-mono
                text-xs
                overflow-auto
                p-4
                flex
                flex-col
                gap-3
            `,children:[n.jsx("div",{className:`
                    text-cyan-300
                    font-semibold
                `,children:"HHS Runtime Console"}),n.jsx("pre",{className:`
                    whitespace-pre-wrap
                    break-all
                    opacity-70
                `,children:JSON.stringify(r,null,2)})]})},b=({runtimeOS:e})=>n.jsxs("div",{className:`
                w-full
                h-full
                overflow-auto
                bg-neutral-950
                text-white
                font-mono
                text-xs
                p-4
            `,children:[n.jsx("div",{className:`
                    text-cyan-400
                    font-semibold
                    mb-4
                `,children:"Runtime Graph Debugger"}),n.jsx("pre",{className:`
                    whitespace-pre-wrap
                    break-all
                    opacity-70
                `,children:JSON.stringify(e.store.getGraphNodes(),null,2)})]}),h=()=>n.jsxs("div",{className:`
                w-full
                h-full
                bg-neutral-950
                text-white
                p-6
                overflow-auto
            `,children:[n.jsx("div",{className:`
                    text-purple-400
                    text-lg
                    font-semibold
                    mb-6
                `,children:"Tensor Inspector"}),n.jsx("div",{className:`
                    grid
                    grid-cols-3
                    gap-4
                `,children:Array.from({length:9}).map((e,r)=>n.jsx("div",{className:`
                                aspect-square
                                rounded-xl
                                border
                                border-neutral-800
                                bg-neutral-900
                                flex
                                items-center
                                justify-center
                                text-xl
                                font-mono
                            `,children:r+1},r))})]}),j=({runtimeOS:e})=>{const r=e.store.getTimeline();return n.jsxs("div",{className:`
                w-full
                h-full
                overflow-auto
                bg-black
                text-green-400
                font-mono
                text-xs
                p-4
                flex
                flex-col
                gap-2
            `,children:[n.jsx("div",{className:`
                    text-green-300
                    font-semibold
                    mb-2
                `,children:"Replay Timeline"}),r.slice().reverse().map((t,u)=>n.jsxs("div",{className:`
                                    border-b
                                    border-neutral-900
                                    pb-2
                                `,children:[n.jsx("div",{children:t.event_type}),n.jsxs("div",{className:`
                                        opacity-50
                                    `,children:["seq:"," ",t.sequence_id]})]},u))]})},i=({label:e})=>n.jsxs("div",{className:`
                w-full
                h-full
                flex
                items-center
                justify-center
                bg-neutral-950
                text-cyan-400
                font-mono
                text-sm
            `,children:["loading_runtime_app:"," ",e]}),v=()=>n.jsx(o,{title:"Calculator Surface Missing",description:`
                upstream runtime calculator module
                not yet available
            `}),g=()=>n.jsx(o,{title:`
                Graph Projection Missing
            `,description:`
                upstream graph projection
                module not yet available
            `}),_=()=>n.jsx(o,{title:`
                Breadboard Missing
            `,description:`
                upstream breadboard
                module not yet available
            `}),w=()=>null,o=({title:e,description:r})=>n.jsx("div",{className:`
                w-full
                h-full
                bg-neutral-950
                flex
                items-center
                justify-center
                p-8
            `,children:n.jsxs("div",{className:`
                    max-w-md
                    rounded-2xl
                    border
                    border-neutral-800
                    bg-neutral-900
                    p-6
                    text-center
                    flex
                    flex-col
                    gap-4
                `,children:[n.jsx("div",{className:`
                        text-lg
                        text-yellow-400
                        font-semibold
                    `,children:e}),n.jsx("div",{className:`
                        text-sm
                        text-neutral-400
                        leading-relaxed
                    `,children:r})]})}),y=({applicationId:e})=>n.jsxs("div",{className:`
                w-full
                h-full
                flex
                items-center
                justify-center
                bg-neutral-950
                text-neutral-500
                font-mono
                text-sm
            `,children:["unknown_application:"," ",e]});export{R as RuntimeWindowContent};
//# sourceMappingURL=RuntimeWindowContent-BgfP_l8-.js.map
