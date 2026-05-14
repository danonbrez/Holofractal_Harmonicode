from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hhs_runtime.runtime_ws import (

    runtime_stream,

    replay_stream,

    graph_stream,

    transport_stream
)

# =========================================================
# FastAPI Runtime Authority
# =========================================================

app = FastAPI()

# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)

# =========================================================
# Runtime Routes
# =========================================================

@app.get("/")
async def root():

    return {

        "runtime":
            "online"
    }

# =========================================================
# Runtime WebSockets
# =========================================================

@app.websocket("/ws/runtime")
async def ws_runtime(websocket):

    await runtime_stream(
        websocket
    )

@app.websocket("/ws/replay")
async def ws_replay(websocket):

    await replay_stream(
        websocket
    )

@app.websocket("/ws/graph")
async def ws_graph(websocket):

    await graph_stream(
        websocket
    )

@app.websocket("/ws/transport")
async def ws_transport(websocket):

    await transport_stream(
        websocket
    )