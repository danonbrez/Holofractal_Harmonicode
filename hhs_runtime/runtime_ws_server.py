from fastapi import FastAPI
from fastapi.websockets import WebSocket
from fastapi.websockets import WebSocketDisconnect

import asyncio
import json
import time

app = FastAPI()

# =========================================================
# Runtime Stream
# =========================================================

@app.websocket("/ws/runtime")
async def runtime_stream(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            payload = {

                "type":
                    "runtime",

                "timestamp":
                    time.time(),

                "status":
                    "online",

                "phase":
                    "runtime_loop"
            }

            await websocket.send_text(
                json.dumps(payload)
            )

            await asyncio.sleep(1)

    except WebSocketDisconnect:

        print(
            "[ws/runtime] disconnected"
        )

# =========================================================
# Replay Stream
# =========================================================

@app.websocket("/ws/replay")
async def replay_stream(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            payload = {

                "type":
                    "replay",

                "timestamp":
                    time.time(),

                "replay":
                    "active"
            }

            await websocket.send_text(
                json.dumps(payload)
            )

            await asyncio.sleep(1)

    except WebSocketDisconnect:

        print(
            "[ws/replay] disconnected"
        )

# =========================================================
# Graph Stream
# =========================================================

@app.websocket("/ws/graph")
async def graph_stream(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            payload = {

                "type":
                    "graph",

                "timestamp":
                    time.time(),

                "nodes":
                    12,

                "edges":
                    28
            }

            await websocket.send_text(
                json.dumps(payload)
            )

            await asyncio.sleep(1)

    except WebSocketDisconnect:

        print(
            "[ws/graph] disconnected"
        )

# =========================================================
# Transport Stream
# =========================================================

@app.websocket("/ws/transport")
async def transport_stream(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            payload = {

                "type":
                    "transport",

                "timestamp":
                    time.time(),

                "throughput":
                    1.0
            }

            await websocket.send_text(
                json.dumps(payload)
            )

            await asyncio.sleep(1)

    except WebSocketDisconnect:

        print(
            "[ws/transport] disconnected"
        )