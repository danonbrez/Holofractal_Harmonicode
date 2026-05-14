from fastapi import WebSocket
from fastapi import WebSocketDisconnect

import asyncio
import json
import time

# =========================================================
# Runtime Stream
# =========================================================

async def runtime_stream(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            await websocket.send_json({

                "type":
                    "runtime",

                "timestamp":
                    time.time(),

                "status":
                    "online"
            })

            await asyncio.sleep(1)

    except WebSocketDisconnect:

        print(
            "[runtime] disconnected"
        )

# =========================================================
# Replay Stream
# =========================================================

async def replay_stream(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            await websocket.send_json({

                "type":
                    "replay",

                "timestamp":
                    time.time()
            })

            await asyncio.sleep(1)

    except WebSocketDisconnect:

        print(
            "[replay] disconnected"
        )

# =========================================================
# Graph Stream
# =========================================================

async def graph_stream(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            await websocket.send_json({

                "type":
                    "graph",

                "nodes":
                    12,

                "edges":
                    24
            })

            await asyncio.sleep(1)

    except WebSocketDisconnect:

        print(
            "[graph] disconnected"
        )

# =========================================================
# Transport Stream
# =========================================================

async def transport_stream(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            await websocket.send_json({

                "type":
                    "transport",

                "throughput":
                    1.0
            })

            await asyncio.sleep(1)

    except WebSocketDisconnect:

        print(
            "[transport] disconnected"
        )