"use strict";
const $ = id => document.getElementById(id);
const pretty = value => JSON.stringify(value, null, 2);
function bridgeRequest(method, path, body = {}) {
  if (!window.HhsBridge) return {ok:false,error_code:"RUNTIME_BINDING_MISMATCH",description:"Android bridge unavailable"};
  const response = JSON.parse(window.HhsBridge.request(method, path, JSON.stringify(body)));
  return response.body || response;
}
function show(id, value){ $(id).textContent = pretty(value); }
document.querySelectorAll("nav button").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll("nav button,.panel").forEach(x => x.classList.remove("active"));
  button.classList.add("active"); $(button.dataset.panel).classList.add("active");
}));
$("connect").addEventListener("click", () => {
  try { window.HhsBridge.configure($("endpoint").value, $("token").value); show("statusOutput", bridgeRequest("GET","/api/v1/status")); }
  catch(error){ show("statusOutput",{ok:false,error_code:"AUTHORITY_INSUFFICIENT",description:String(error)}); }
});
$("refreshStatus").addEventListener("click",()=>show("statusOutput",bridgeRequest("GET","/api/v1/status")));
$("ingestSource").addEventListener("click",()=>show("ingestOutput",bridgeRequest("POST","/api/v1/ingest",{name:$("sourceName").value,namespace:$("namespace").value,mime_type:$("mimeType").value,text:$("sourceText").value})));
$("runQuery").addEventListener("click",()=>show("queryOutput",bridgeRequest("POST","/api/v1/query",{question:$("question").value,namespace:$("namespace").value})));
$("searchSymbol").addEventListener("click",()=>show("queryOutput",bridgeRequest("POST","/api/v1/search",{text:$("question").value.trim().split(/\s+/).pop(),symbol:true,namespace:$("namespace").value})));
$("databaseStatus").addEventListener("click",()=>show("receiptOutput",bridgeRequest("GET","/api/v1/database/status")));
$("receiptChain").addEventListener("click",()=>show("receiptOutput",bridgeRequest("POST","/api/v1/validate",{target:"receipt"})));
$("runCommand").addEventListener("click",()=>{
  const line=$("command").value.trim(); const [command,...rest]=line.match(/(?:[^\s"]+|"[^"]*")+/g)||[]; let value;
  if(command==="status") value=bridgeRequest("GET","/api/v1/status");
  else if(command==="query") value=bridgeRequest("POST","/api/v1/query",{question:rest.join(" ").replaceAll('"','')});
  else if(command==="search") value=bridgeRequest("POST","/api/v1/search",{text:rest.join(" ").replaceAll('"','')});
  else if(command==="validate"&&rest[0]) value=bridgeRequest("POST","/api/v1/validate",{target:"source",id:rest[0]});
  else value={ok:false,error_code:"CLI_UNREACHABLE",description:"Supported embedded commands: status, query, search, validate"};
  show("commandOutput",value);
});
window.hhsReceiveSharedText = text => { $("sourceText").value=text; document.querySelector('[data-panel="ingest"]').click(); };
try { $("nativeState").textContent = "Native runtime: " + JSON.parse(window.HhsBridge.nativeStatus()).abi; }
catch(error){ $("nativeState").textContent="Native runtime unavailable"; }
