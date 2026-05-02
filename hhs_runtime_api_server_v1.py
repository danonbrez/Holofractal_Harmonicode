from fastapi import FastAPI
import time
import hashlib

app = FastAPI()

# incremental pipeline restore

def _interp(x): return {"expr": x, "status": "ok"}

def _solve(i): return {"expr": i["expr"], "status": "ok"}

@app.get("/api/status")
def status():
    return {"ok": True, "time": time.time()}

@app.post("/api/agent/run-loop")
def run(req: dict):
    expr = req.get("expression", "")

    i = _interp(expr)
    s = _solve(i)

    return {
        "input": expr,
        "interpreted": i,
        "solved": s,
        "hash72": hashlib.sha256(expr.encode()).hexdigest()[:72]
    }
