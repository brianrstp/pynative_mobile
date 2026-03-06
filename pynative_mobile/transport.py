from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Any
import threading
import asyncio
import uvicorn

try:
    import socketio
except ImportError:
    socketio = None


class BridgeServer:

    def __init__(self, host: str = "0.0.0.0", port: int = 8000, auth_token: str | None = None) -> None:
        self.app = FastAPI()
        self.host = host
        self.port = port
        self.auth_token = auth_token
        self._connections: List[WebSocket] = []

        @self.app.websocket("/ws")
        async def websocket_endpoint(ws: WebSocket):
            await ws.accept()
            self._connections.append(ws)
            try:
                while True:
                    text = await ws.receive_text()
                    try:
                        import json

                        msg = json.loads(text)
                        if isinstance(msg, dict) and msg.get("type") == "log":
                            print(f"[Device] {msg.get('message')}")
                    except Exception:
                        pass
            except WebSocketDisconnect:
                self._connections.remove(ws)

    def broadcast(self, message: str) -> None:
        loop = asyncio.get_event_loop()
        for ws in list(self._connections):
            asyncio.run_coroutine_threadsafe(ws.send_text(message), loop)

    def start(self, log_level: str = "info") -> None:
        thread = threading.Thread(
            target=uvicorn.run,
            args=(self.app,),
            kwargs={"host": self.host, "port": self.port, "log_level": log_level},
            daemon=True,
        )
        thread.start()


class SocketIOBridge:
    def __init__(self, host: str = "0.0.0.0", port: int = 8000, auth_token: str | None = None) -> None:
        if socketio is None: 
            raise RuntimeError("python-socketio is required for SocketIOBridge")

        self.auth_token = auth_token
        self.sio = socketio.AsyncServer(async_mode="asgi")
        self.app = FastAPI()
        self.host = host
        self.port = port

        self.app.mount("/", socketio.ASGIApp(self.sio))

        @self.sio.event
        async def connect(sid, environ):
            print(f"SocketIO client connected: {sid}")
            if self.auth_token:
                qs = environ.get("QUERY_STRING", "")
                params = dict(item.split("=") for item in qs.split("&") if item)
                token = params.get("token")
                if token != self.auth_token:
                    await self.sio.disconnect(sid)

        @self.sio.event
        async def disconnect(sid):
            print(f"SocketIO client disconnected: {sid}")

        @self.sio.on("log")
        async def on_log(sid, message):
            print(f"[Device] {message}")

    def broadcast(self, message: Any) -> None:
        asyncio.create_task(self.sio.emit("update", message))

    def start(self, log_level: str = "info") -> None:
        thread = threading.Thread(
            target=uvicorn.run,
            args=(self.app,),
            kwargs={"host": self.host, "port": self.port, "log_level": log_level},
            daemon=True,
        )
        thread.start()