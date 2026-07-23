export const TEMPLATES=[
{id:"operator-default",label:"Operator Default",mode:"operator",camera:{yaw:.1,pitch:-.08,distance:13.5,center:[0,0,0]},autoRotate:true,feature:"dashboard"},
{id:"analytical-deep-dive",label:"Analytical Deep Dive",mode:"analytical",camera:{yaw:-.3,pitch:.18,distance:11.5,center:[0,0,0]},autoRotate:false,feature:"metrics"},
{id:"creator-workbench",label:"Creator Workbench",mode:"creator",camera:{yaw:.34,pitch:-.15,distance:12.4,center:[0,0,0]},autoRotate:false,feature:"settings"},
{id:"minimal-focus",label:"Minimal Focus",mode:"overview",camera:{yaw:0,pitch:0,distance:10.8,center:[0,0,0]},autoRotate:true,feature:"lattice"},
{id:"command-center",label:"Command Center",mode:"operator",camera:{yaw:-.1,pitch:-.18,distance:14.5,center:[0,0,0]},autoRotate:true,feature:"runtime"},
{id:"game-world",label:"Game World",mode:"game",camera:{yaw:0,pitch:-.02,distance:8.4,center:[0,0,0]},autoRotate:false,feature:"fields"},
{id:"knowledge-explorer",label:"Knowledge Explorer",mode:"analytical",camera:{yaw:.45,pitch:.14,distance:12.8,center:[0,0,0]},autoRotate:true,feature:"knowledge"},
{id:"runtime-diagnostics",label:"Runtime Diagnostics",mode:"analytical",camera:{yaw:-.45,pitch:.05,distance:11.2,center:[0,0,0]},autoRotate:false,feature:"runtime"},
{id:"mobile-compact",label:"Mobile Compact",mode:"overview",camera:{yaw:0,pitch:-.08,distance:14,center:[0,0,0]},autoRotate:true,feature:"dashboard"}]
export function templateById(id){return TEMPLATES.find(t=>t.id===id)??TEMPLATES[0]}
