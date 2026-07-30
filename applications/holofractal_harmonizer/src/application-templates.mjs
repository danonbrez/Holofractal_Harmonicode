const lines = (...values) => `${values.join('\n')}\n`;

function project(id, label, description, entrypoint, files) {
  return Object.freeze({ id, label, description, entrypoint, files: Object.freeze(files) });
}

const BASE_STYLE = lines(
  ':root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }',
  '* { box-sizing: border-box; }',
  'body { margin: 0; min-height: 100vh; background: radial-gradient(circle at 50% -10%, #3a2818, #15100c 55%); color: #f4eadb; }',
  'button, input, textarea, select { font: inherit; }',
  'button { cursor: pointer; border: 1px solid #8d6a39; border-radius: 10px; background: #392916; color: #f7d796; padding: .72rem 1rem; }',
  'button:hover { background: #4b351b; }',
  '.app-shell { width: min(980px, calc(100% - 24px)); margin: 0 auto; padding: 24px 0 48px; }',
  '.app-card { border: 1px solid #5f4930; border-radius: 18px; background: rgba(35, 27, 20, .94); box-shadow: 0 24px 70px rgba(0,0,0,.36); overflow: hidden; }',
  '.app-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 18px; border-bottom: 1px solid #5f4930; }',
  '.app-header h1 { margin: 0; font-size: clamp(1.1rem, 4vw, 1.65rem); }',
  '.app-header small { color: #b9a68c; }',
  '.app-body { padding: 18px; }',
  '.muted { color: #b9a68c; }',
  '@media (max-width: 640px) { .app-header { align-items: flex-start; flex-direction: column; } .app-body { padding: 12px; } }'
);

const WEB_HTML = lines(
  '<!doctype html>',
  '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
  '<title>My Application</title><link rel="stylesheet" href="./style.css"></head>',
  '<body><main class="app-shell"><section class="app-card"><header class="app-header"><div><small>READY PROJECT</small><h1 id="title">My Application</h1></div><button id="action">Run Action</button></header>',
  '<div class="app-body"><p>Edit <code>index.html</code>, <code>style.css</code>, and <code>app.js</code>. Press Build & Preview to run changes.</p><output id="output">Application ready.</output></div></section></main>',
  '<script src="./app.js"></script></body></html>'
);
const WEB_JS = lines(
  'const output = document.querySelector("#output");',
  'document.querySelector("#action").addEventListener("click", () => {',
  '  output.textContent = `Application action ran at ${new Date().toLocaleTimeString()}.`;',
  '});'
);

const PONG_HTML = lines(
  '<!doctype html>',
  '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
  '<title>Harmonic Pong</title><link rel="stylesheet" href="./style.css"></head>',
  '<body><main class="app-shell"><section class="app-card"><header class="app-header"><div><small>PLAYABLE GAME</small><h1>Harmonic Pong</h1></div><div class="score"><b id="playerScore">0</b><span>:</span><b id="cpuScore">0</b></div></header>',
  '<div class="app-body"><canvas id="game" width="720" height="420" aria-label="Playable Pong game"></canvas><div class="controls"><button id="start">Start / Reset</button><span>Move with pointer, touch, W/S, or ↑/↓.</span></div></div></section></main>',
  '<script src="./app.js"></script></body></html>'
);
const PONG_STYLE = `${BASE_STYLE}${lines(
  '#game { width: 100%; aspect-ratio: 12/7; display: block; border: 1px solid #9b7542; border-radius: 12px; background: #0b0907; touch-action: none; }',
  '.score { display: flex; align-items: center; gap: .7rem; font-size: 1.8rem; color: #f2bb55; }',
  '.controls { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 12px; color: #b9a68c; }',
  '@media (max-width: 620px) { .controls { align-items: stretch; flex-direction: column; } }'
)}`;
const PONG_JS = lines(
  'const canvas = document.querySelector("#game");',
  'const ctx = canvas.getContext("2d");',
  'const playerScore = document.querySelector("#playerScore");',
  'const cpuScore = document.querySelector("#cpuScore");',
  'const state = { running: false, player: 170, cpu: 170, playerPoints: 0, cpuPoints: 0, keys: new Set(), ball: { x: 360, y: 210, vx: 5.2, vy: 3.2 } };',
  'function resetBall(direction = 1) { state.ball = { x: 360, y: 210, vx: 5.2 * direction, vy: (Math.random() * 5) - 2.5 }; }',
  'function reset() { state.playerPoints = 0; state.cpuPoints = 0; state.player = 170; state.cpu = 170; playerScore.textContent = "0"; cpuScore.textContent = "0"; resetBall(Math.random() > .5 ? 1 : -1); state.running = true; }',
  'function movePlayer(clientY) { const rect = canvas.getBoundingClientRect(); state.player = Math.max(0, Math.min(340, ((clientY - rect.top) / rect.height) * 420 - 40)); }',
  'canvas.addEventListener("pointermove", event => movePlayer(event.clientY));',
  'canvas.addEventListener("pointerdown", event => { canvas.setPointerCapture(event.pointerId); movePlayer(event.clientY); state.running = true; });',
  'addEventListener("keydown", event => state.keys.add(event.key.toLowerCase()));',
  'addEventListener("keyup", event => state.keys.delete(event.key.toLowerCase()));',
  'document.querySelector("#start").addEventListener("click", reset);',
  'function update() {',
  '  if (state.keys.has("w") || state.keys.has("arrowup")) state.player -= 6;',
  '  if (state.keys.has("s") || state.keys.has("arrowdown")) state.player += 6;',
  '  state.player = Math.max(0, Math.min(340, state.player));',
  '  if (!state.running) return;',
  '  const ball = state.ball; ball.x += ball.vx; ball.y += ball.vy;',
  '  if (ball.y < 9 || ball.y > 411) { ball.vy *= -1; ball.y = Math.max(9, Math.min(411, ball.y)); }',
  '  state.cpu += Math.sign(ball.y - (state.cpu + 40)) * 3.7; state.cpu = Math.max(0, Math.min(340, state.cpu));',
  '  if (ball.x < 34 && ball.x > 18 && ball.y > state.player && ball.y < state.player + 80 && ball.vx < 0) { ball.vx = Math.abs(ball.vx) * 1.035; ball.vy += (ball.y - state.player - 40) * .045; }',
  '  if (ball.x > 686 && ball.x < 702 && ball.y > state.cpu && ball.y < state.cpu + 80 && ball.vx > 0) { ball.vx = -Math.abs(ball.vx) * 1.035; ball.vy += (ball.y - state.cpu - 40) * .045; }',
  '  if (ball.x < -12) { state.cpuPoints += 1; cpuScore.textContent = state.cpuPoints; resetBall(1); }',
  '  if (ball.x > 732) { state.playerPoints += 1; playerScore.textContent = state.playerPoints; resetBall(-1); }',
  '}',
  'function draw() {',
  '  ctx.clearRect(0, 0, 720, 420); ctx.fillStyle = "#0b0907"; ctx.fillRect(0, 0, 720, 420);',
  '  ctx.strokeStyle = "#4f3a24"; ctx.setLineDash([10, 12]); ctx.beginPath(); ctx.moveTo(360, 0); ctx.lineTo(360, 420); ctx.stroke(); ctx.setLineDash([]);',
  '  ctx.fillStyle = "#e8a43c"; ctx.fillRect(18, state.player, 14, 80); ctx.fillStyle = "#b8d07a"; ctx.fillRect(688, state.cpu, 14, 80);',
  '  ctx.beginPath(); ctx.arc(state.ball.x, state.ball.y, 9, 0, Math.PI * 2); ctx.fillStyle = "#fff4d6"; ctx.fill();',
  '}',
  'function loop() { update(); draw(); requestAnimationFrame(loop); }',
  'reset(); loop();'
);

const CALCULATOR_HTML = lines(
  '<!doctype html>',
  '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
  '<title>Calculator</title><link rel="stylesheet" href="./style.css"></head>',
  '<body><main class="calculator" aria-label="Working calculator"><div class="display"><small id="history">Ready</small><output id="display">0</output></div><div id="keys" class="keys"></div></main><script src="./app.js"></script></body></html>'
);
const CALCULATOR_STYLE = lines(
  ':root { color-scheme: dark; font-family: Inter, system-ui, sans-serif; } * { box-sizing: border-box; }',
  'body { margin: 0; min-height: 100vh; display: grid; place-items: center; background: radial-gradient(circle at top, #3a2818, #15100c 58%); color: #f4eadb; }',
  '.calculator { width: min(390px, calc(100% - 24px)); padding: 16px; border: 1px solid #6f5332; border-radius: 22px; background: #241b14; box-shadow: 0 28px 80px #0008; }',
  '.display { min-height: 126px; display: grid; align-content: end; justify-items: end; padding: 18px; border-radius: 15px; background: #0f0c09; overflow: hidden; }',
  '.display small { color: #9f907d; min-height: 1.4em; } .display output { max-width: 100%; overflow-wrap: anywhere; font-size: 2.5rem; color: #f2c86f; }',
  '.keys { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 12px; }',
  'button { min-height: 58px; border: 1px solid #5c4731; border-radius: 14px; background: #33271c; color: #f4eadb; font-size: 1.1rem; }',
  'button:hover { background: #46331f; } button[data-kind="operator"] { color: #f2c86f; } button[data-value="="] { background: #80571d; color: white; }'
);
const CALCULATOR_JS = lines(
  'const display = document.querySelector("#display"); const history = document.querySelector("#history"); const keys = document.querySelector("#keys");',
  'const labels = ["C","(",")","÷","7","8","9","×","4","5","6","−","1","2","3","+","0",".","⌫","="]; let expression = "";',
  'for (const label of labels) { const button = document.createElement("button"); button.textContent = label; button.dataset.value = label; if ("÷×−+".includes(label)) button.dataset.kind = "operator"; keys.append(button); }',
  'function render() { display.textContent = expression || "0"; }',
  'function evaluate() {',
  '  const safe = expression.replaceAll("×", "*").replaceAll("÷", "/").replaceAll("−", "-");',
  '  if (!/^[0-9+\-*/().\s]+$/.test(safe)) throw new Error("Unsupported expression");',
  '  const result = Function(`"use strict"; return (${safe || 0})`)();',
  '  if (!Number.isFinite(result)) throw new Error("Result is not finite");',
  '  history.textContent = expression; expression = String(result); render();',
  '}',
  'keys.addEventListener("click", event => { const value = event.target.dataset.value; if (!value) return; try { if (value === "C") { expression = ""; history.textContent = "Cleared"; } else if (value === "⌫") expression = expression.slice(0, -1); else if (value === "=") evaluate(); else expression += value; render(); } catch (error) { history.textContent = error.message; expression = ""; render(); } });',
  'addEventListener("keydown", event => { if (/^[0-9+\-*/().]$/.test(event.key)) { expression += event.key; render(); } if (event.key === "Enter") { event.preventDefault(); keys.querySelector("[data-value=\"=\"]").click(); } if (event.key === "Backspace") { expression = expression.slice(0,-1); render(); } });'
);

const PUZZLE_HTML = lines(
  '<!doctype html>',
  '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
  '<title>Sliding Puzzle</title><link rel="stylesheet" href="./style.css"></head>',
  '<body><main class="app-shell"><section class="app-card"><header class="app-header"><div><small>PLAYABLE PUZZLE</small><h1>Fifteen Tiles</h1></div><div><b id="moves">0</b> moves</div></header><div class="app-body"><div id="board" class="board" aria-label="Sliding tile puzzle"></div><div class="puzzle-actions"><button id="shuffle">New Puzzle</button><output id="status">Arrange the tiles from 1 to 15.</output></div></div></section></main><script src="./app.js"></script></body></html>'
);
const PUZZLE_STYLE = `${BASE_STYLE}${lines(
  '.board { width: min(560px, 100%); aspect-ratio: 1; margin: auto; display: grid; grid-template-columns: repeat(4, 1fr); gap: 7px; padding: 8px; border: 1px solid #6d5130; border-radius: 16px; background: #100c09; }',
  '.tile { min-width: 0; border-radius: 12px; font-size: clamp(1.1rem, 7vw, 2rem); font-weight: 800; background: linear-gradient(145deg, #5c3d17, #2c2118); color: #ffd985; }',
  '.tile.empty { visibility: hidden; } .puzzle-actions { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 14px; }',
  '@media (max-width: 520px) { .puzzle-actions { align-items: stretch; flex-direction: column; } }'
)}`;
const PUZZLE_JS = lines(
  'const board = document.querySelector("#board"); const moves = document.querySelector("#moves"); const status = document.querySelector("#status"); let cells = []; let moveCount = 0;',
  'function solvableShuffle() { cells = Array.from({length:16}, (_,i) => i); for (let i = 0; i < 160; i += 1) { const empty = cells.indexOf(0); const row = Math.floor(empty/4); const col = empty%4; const options = []; if(row) options.push(empty-4); if(row<3) options.push(empty+4); if(col) options.push(empty-1); if(col<3) options.push(empty+1); const pick = options[Math.floor(Math.random()*options.length)]; [cells[empty],cells[pick]]=[cells[pick],cells[empty]]; } moveCount=0; moves.textContent="0"; status.textContent="Arrange the tiles from 1 to 15."; render(); }',
  'function adjacent(a,b) { return Math.abs(Math.floor(a/4)-Math.floor(b/4)) + Math.abs(a%4-b%4) === 1; }',
  'function render() { board.replaceChildren(); cells.forEach((value,index) => { const button=document.createElement("button"); button.className=`tile ${value ? "" : "empty"}`; button.textContent=value||""; button.disabled=!value; button.onclick=()=>move(index); board.append(button); }); }',
  'function move(index) { const empty=cells.indexOf(0); if(!adjacent(index,empty)) return; [cells[index],cells[empty]]=[cells[empty],cells[index]]; moveCount+=1; moves.textContent=moveCount; render(); if(cells.every((value,index)=>value===((index+1)%16))) status.textContent=`Solved in ${moveCount} moves.`; }',
  'document.querySelector("#shuffle").onclick=solvableShuffle; solvableShuffle();'
);

const DOCUMENT_HTML = lines(
  '<!doctype html>',
  '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
  '<title>Document Studio</title><link rel="stylesheet" href="./style.css"></head>',
  '<body><main class="document-shell"><header><input id="title" value="Untitled Document" aria-label="Document title"><div><button id="saveText">Download TXT</button><button id="saveHtml">Download HTML</button></div></header><article id="editor" contenteditable="true" spellcheck="true"><h1>Start writing</h1><p>This is a real editable document. Your work is saved locally while you type.</p></article><footer><span id="words">0 words</span><span id="saved">Ready</span></footer></main><script src="./app.js"></script></body></html>'
);
const DOCUMENT_STYLE = lines(
  ':root { color-scheme: dark; font-family: Georgia, serif; } * { box-sizing: border-box; }',
  'body { margin: 0; min-height: 100vh; background: #18120d; color: #2a2118; }',
  '.document-shell { width: min(920px, 100%); min-height: 100vh; margin: auto; display: grid; grid-template-rows: auto 1fr auto; background: #f2eadc; box-shadow: 0 0 70px #0008; }',
  'header, footer { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px 18px; background:#2a2018; color:#eadac4; font-family:system-ui,sans-serif; }',
  '#title { min-width:0; flex:1; border:0; border-bottom:1px solid #80613d; background:transparent; color:#f4eadb; font-size:1.1rem; padding:.5rem; }',
  'button { border:1px solid #8c6c42; border-radius:8px; background:#48331c; color:#f8d896; padding:.6rem .8rem; }',
  '#editor { min-height:70vh; padding:clamp(28px,8vw,90px); outline:none; font-size:1.1rem; line-height:1.75; }',
  '#editor:focus { box-shadow: inset 0 0 0 3px #c08a3b55; } @media(max-width:620px){header{align-items:stretch;flex-direction:column} header div{display:flex;gap:6px} header button{flex:1}}'
);
const DOCUMENT_JS = lines(
  'const editor=document.querySelector("#editor"); const title=document.querySelector("#title"); const saved=document.querySelector("#saved"); const words=document.querySelector("#words"); const KEY="hhs-document-studio-v1";',
  'try { const prior=JSON.parse(localStorage.getItem(KEY)||"null"); if(prior){title.value=prior.title;editor.innerHTML=prior.html;} } catch {}',
  'function count(){const value=editor.innerText.trim();words.textContent=`${value ? value.split(/\\s+/).length : 0} words`;}',
  'function persist(){localStorage.setItem(KEY,JSON.stringify({title:title.value,html:editor.innerHTML}));saved.textContent=`Saved ${new Date().toLocaleTimeString()}`;count();}',
  'function download(name,type,content){const url=URL.createObjectURL(new Blob([content],{type}));const link=document.createElement("a");link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}',
  'editor.addEventListener("input",persist);title.addEventListener("input",persist);',
  'document.querySelector("#saveText").onclick=()=>download(`${title.value||"document"}.txt`,"text/plain",editor.innerText);',
  'document.querySelector("#saveHtml").onclick=()=>download(`${title.value||"document"}.html`,"text/html",`<!doctype html><meta charset="utf-8"><title>${title.value}</title><article>${editor.innerHTML}</article>`);',
  'count();'
);

const AUDIO_HTML = lines(
  '<!doctype html>',
  '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
  '<title>Audio Studio</title><link rel="stylesheet" href="./style.css"></head>',
  '<body><main class="app-shell"><section class="app-card"><header class="app-header"><div><small>WEB AUDIO APPLICATION</small><h1>Pattern Synth</h1></div><div class="transport"><button id="play">Play Pattern</button><button id="record">Record</button></div></header><div class="app-body"><div id="pads" class="pads"></div><label>Tempo <input id="tempo" type="range" min="60" max="180" value="108"><output id="tempoValue">108 BPM</output></label><div id="steps" class="steps"></div><p id="audioStatus" class="muted">Tap a pad to enable audio. Recordings download as WebM audio.</p></div></section></main><script src="./app.js"></script></body></html>'
);
const AUDIO_STYLE = `${BASE_STYLE}${lines(
  '.transport { display:flex; gap:8px; } .pads { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:18px; }',
  '.pad { min-height:82px; font-size:1rem; } .steps { display:grid; grid-template-columns:repeat(8,1fr); gap:6px; margin-top:16px; }',
  '.step { min-height:46px; padding:0; background:#1b1510; } .step.active { background:#80571d; box-shadow:0 0 18px #d28a2d55; }',
  'label { display:grid; grid-template-columns:auto 1fr auto; align-items:center; gap:12px; } @media(max-width:620px){.pads{grid-template-columns:repeat(2,1fr)}.transport{width:100%}.transport button{flex:1}}'
)}`;
const AUDIO_JS = lines(
  'const notes=[261.63,329.63,392,523.25]; const labels=["C4","E4","G4","C5"]; const pattern=[true,false,true,false,true,true,false,true];',
  'const pads=document.querySelector("#pads"); const steps=document.querySelector("#steps"); const status=document.querySelector("#audioStatus"); const tempo=document.querySelector("#tempo"); let context; let destination; let recorder; let chunks=[]; let playing=false;',
  'function audio(){ if(!context){context=new AudioContext();destination=context.createMediaStreamDestination();} return context; }',
  'function tone(frequency,duration=.18){const ctx=audio();const osc=ctx.createOscillator();const gain=ctx.createGain();osc.type="triangle";osc.frequency.value=frequency;gain.gain.setValueAtTime(.0001,ctx.currentTime);gain.gain.exponentialRampToValueAtTime(.32,ctx.currentTime+.01);gain.gain.exponentialRampToValueAtTime(.0001,ctx.currentTime+duration);osc.connect(gain);gain.connect(ctx.destination);gain.connect(destination);osc.start();osc.stop(ctx.currentTime+duration+.03);}',
  'labels.forEach((label,index)=>{const button=document.createElement("button");button.className="pad";button.textContent=label;button.onclick=()=>tone(notes[index],.35);pads.append(button);});',
  'pattern.forEach((active,index)=>{const button=document.createElement("button");button.className=`step ${active?"active":""}`;button.textContent=index+1;button.onclick=()=>button.classList.toggle("active");steps.append(button);});',
  'tempo.oninput=()=>document.querySelector("#tempoValue").textContent=`${tempo.value} BPM`;',
  'document.querySelector("#play").onclick=async()=>{if(playing)return;playing=true;const buttons=[...steps.children];for(let i=0;i<buttons.length;i+=1){buttons.forEach((b,n)=>b.style.outline=n===i?"2px solid #ffd27b":"");if(buttons[i].classList.contains("active"))tone(notes[i%notes.length],.12);await new Promise(r=>setTimeout(r,60000/Number(tempo.value)/2));}buttons.forEach(b=>b.style.outline="");playing=false;};',
  'document.querySelector("#record").onclick=async event=>{audio();if(!recorder||recorder.state==="inactive"){chunks=[];recorder=new MediaRecorder(destination.stream);recorder.ondataavailable=e=>chunks.push(e.data);recorder.onstop=()=>{const url=URL.createObjectURL(new Blob(chunks,{type:recorder.mimeType}));const link=document.createElement("a");link.href=url;link.download="hhs-pattern.webm";link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent="Recording downloaded.";};recorder.start();event.target.textContent="Stop & Download";status.textContent="Recording synth output…";}else{recorder.stop();event.target.textContent="Record";}};'
);

const VIDEO_HTML = lines(
  '<!doctype html>',
  '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
  '<title>Video Studio</title><link rel="stylesheet" href="./style.css"></head>',
  '<body><main class="app-shell"><section class="app-card"><header class="app-header"><div><small>CANVAS VIDEO APPLICATION</small><h1>Motion Title Studio</h1></div><div><button id="record">Record Video</button></div></header><div class="app-body"><canvas id="stage" width="960" height="540"></canvas><div class="video-controls"><label>Title <input id="title" value="HHS Motion"></label><label>Speed <input id="speed" type="range" min="1" max="10" value="4"></label><label>Accent <input id="accent" type="color" value="#e0a63c"></label></div><p id="videoStatus" class="muted">The live canvas can be recorded and downloaded as WebM video.</p></div></section></main><script src="./app.js"></script></body></html>'
);
const VIDEO_STYLE = `${BASE_STYLE}${lines(
  '#stage { width:100%; display:block; border:1px solid #6b4e2e; border-radius:14px; background:#080604; }',
  '.video-controls { display:grid; grid-template-columns:2fr 1fr 1fr; gap:10px; margin-top:14px; }',
  '.video-controls label { display:grid; gap:5px; color:#b9a68c; font-size:.84rem; }',
  '.video-controls input { min-height:42px; border:1px solid #60472e; border-radius:8px; background:#17110d; color:#f4eadb; padding:.45rem; }',
  '@media(max-width:620px){.video-controls{grid-template-columns:1fr}}'
)}`;
const VIDEO_JS = lines(
  'const canvas=document.querySelector("#stage");const ctx=canvas.getContext("2d");const title=document.querySelector("#title");const speed=document.querySelector("#speed");const accent=document.querySelector("#accent");const status=document.querySelector("#videoStatus");let phase=0;let recorder;let chunks=[];',
  'function frame(){phase+=Number(speed.value)*.006;const gradient=ctx.createLinearGradient(0,0,960,540);gradient.addColorStop(0,"#120d09");gradient.addColorStop(1,"#2b1b0e");ctx.fillStyle=gradient;ctx.fillRect(0,0,960,540);for(let i=0;i<18;i+=1){const angle=phase+i*.61;const x=480+Math.cos(angle)*240;const y=270+Math.sin(angle*1.4)*150;ctx.beginPath();ctx.arc(x,y,8+(i%5)*4,0,Math.PI*2);ctx.fillStyle=`${accent.value}${Math.round(70+i*8).toString(16).padStart(2,"0")}`;ctx.fill();}ctx.textAlign="center";ctx.textBaseline="middle";ctx.font="700 72px system-ui";ctx.fillStyle="#fff3da";ctx.fillText(title.value||"Untitled",480,270);ctx.font="24px system-ui";ctx.fillStyle=accent.value;ctx.fillText("Canvas motion rendered in real time",480,340);requestAnimationFrame(frame);}frame();',
  'document.querySelector("#record").onclick=event=>{if(!recorder||recorder.state==="inactive"){chunks=[];const stream=canvas.captureStream(30);recorder=new MediaRecorder(stream,{mimeType:MediaRecorder.isTypeSupported("video/webm;codecs=vp9")?"video/webm;codecs=vp9":"video/webm"});recorder.ondataavailable=e=>chunks.push(e.data);recorder.onstop=()=>{const url=URL.createObjectURL(new Blob(chunks,{type:recorder.mimeType}));const link=document.createElement("a");link.href=url;link.download="hhs-motion.webm";link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent="Video downloaded.";};recorder.start();event.target.textContent="Stop & Download";status.textContent="Recording 30 FPS canvas video…";}else{recorder.stop();event.target.textContent="Record Video";}};'
);

export const APPLICATION_TEMPLATES = Object.freeze({
  web: project('web', 'Web Application', 'HTML, CSS and JavaScript with live preview.', 'web/index.html', [
    ['web/index.html', 'HTML', WEB_HTML], ['web/style.css', 'SOURCE_CODE', BASE_STYLE], ['web/app.js', 'SOURCE_CODE', WEB_JS],
    ['README.md', 'MARKDOWN', '# Web Application\n\nEdit the project, run it in Application Preview, compile targets, and export the complete ZIP.\n'],
  ]),
  pong: project('pong', 'Pong Game', 'A complete playable canvas game with pointer, touch and keyboard controls.', 'pong/index.html', [
    ['pong/index.html', 'HTML', PONG_HTML], ['pong/style.css', 'SOURCE_CODE', PONG_STYLE], ['pong/app.js', 'SOURCE_CODE', PONG_JS],
    ['README.md', 'MARKDOWN', '# Harmonic Pong\n\nPlayable source project. Change physics, controls, graphics or scoring and rebuild.\n'],
  ]),
  calculator: project('calculator', 'Calculator', 'A functional keyboard and touch calculator application.', 'calculator/index.html', [
    ['calculator/index.html', 'HTML', CALCULATOR_HTML], ['calculator/style.css', 'SOURCE_CODE', CALCULATOR_STYLE], ['calculator/app.js', 'SOURCE_CODE', CALCULATOR_JS],
  ]),
  puzzle: project('puzzle', 'Puzzle Game', 'A solvable 4×4 sliding-tile puzzle with move tracking.', 'puzzle/index.html', [
    ['puzzle/index.html', 'HTML', PUZZLE_HTML], ['puzzle/style.css', 'SOURCE_CODE', PUZZLE_STYLE], ['puzzle/app.js', 'SOURCE_CODE', PUZZLE_JS],
  ]),
  document: project('document', 'Text Document', 'A real rich-text document editor with local autosave and file download.', 'document/index.html', [
    ['document/index.html', 'HTML', DOCUMENT_HTML], ['document/style.css', 'SOURCE_CODE', DOCUMENT_STYLE], ['document/app.js', 'SOURCE_CODE', DOCUMENT_JS],
    ['content/document.md', 'MARKDOWN', '# Document Source\n\nThis Markdown file can be edited and compiled alongside the interactive document application.\n'],
  ]),
  audio: project('audio', 'Audio Studio', 'A Web Audio synthesizer, sequencer and downloadable recorder.', 'audio/index.html', [
    ['audio/index.html', 'HTML', AUDIO_HTML], ['audio/style.css', 'SOURCE_CODE', AUDIO_STYLE], ['audio/app.js', 'SOURCE_CODE', AUDIO_JS],
    ['audio/project.json', 'JSON', '{\n  "type": "audio-application",\n  "output": "webm-audio",\n  "sample_rate": "browser-device"\n}\n'],
  ]),
  video: project('video', 'Video Studio', 'A real-time canvas animation editor with downloadable WebM recording.', 'video/index.html', [
    ['video/index.html', 'HTML', VIDEO_HTML], ['video/style.css', 'SOURCE_CODE', VIDEO_STYLE], ['video/app.js', 'SOURCE_CODE', VIDEO_JS],
    ['video/project.json', 'JSON', '{\n  "type": "canvas-video-application",\n  "output": "webm-video",\n  "fps": 30\n}\n'],
  ]),
  automation: project('automation', 'HHS Automation', 'HARMONICODE source with Python and JSON project adapters.', 'src/main.hhs', [
    ['src/main.hhs', 'SOURCE_CODE', 'a²=1\nb²=2\nc²=3\nP=72\np=64\nq=81\nΔ=P²-pq\n(P²-pq)-Δ=0\n'],
    ['src/adapter.py', 'SOURCE_CODE', 'def main() -> None:\n    print("HHS automation adapter ready")\n\nif __name__ == "__main__":\n    main()\n'],
    ['project.json', 'JSON', '{\n  "schema": "HHS_MULTIMODAL_PROJECT_V1",\n  "entrypoint": "src/main.hhs"\n}\n'],
  ]),
});

export function applicationTemplateList() {
  return Object.values(APPLICATION_TEMPLATES);
}

export function materializeApplicationTemplate(id) {
  const template = APPLICATION_TEMPLATES[id] || APPLICATION_TEMPLATES.web;
  return {
    ...template,
    files: template.files.map(([path, mediaType, content]) => ({
      path,
      name: path.split('/').at(-1),
      mediaType,
      content,
      dirty: true,
    })),
  };
}
