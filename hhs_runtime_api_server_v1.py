from fastapi import FastAPI
import time

app = FastAPI()

@app.get("/api/status")
def status():
    return {"ok": True, "time": time.time()}

@app.post("/api/agent/run-loop")
def run(req: dict):
    expr = req.get("expression", "")
    return {"input": expr, "final": expr}
