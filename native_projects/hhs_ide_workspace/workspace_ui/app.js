/* Every human or agent action becomes a HHS_UNIFIED_RUNTIME_REQUEST_V1.
   No GUI state, LLM response, or external client may mutate Runtime state directly. */
const API = "/api/hhs/v1";
async function send(path, envelope) {
  const response = await fetch(`${API}/${path}`, {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify(envelope)
  });
  return response.json();
}
function subscribe(after = 0) {
  return new WebSocket(`${location.origin.replace("http", "ws")}${API}/events?after=${after}`);
}
window.HHSWorkspace = {send, subscribe};
document.getElementById("StatusBar").textContent = "Runtime API: unified agent boundary ready";
