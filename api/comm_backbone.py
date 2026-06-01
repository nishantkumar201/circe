from fastapi import FastAPI, WebSocket
import uvicorn
from fastapi.responses import FileResponse


class CommBackbone(FastAPI):
    def __init__(self):
        super().__init__()
        self._register_endpoints()
        self._development = True

    def _register_endpoints(self):
        self.get("/")(self.dashboard)
        self.get("/status")(self.status)
        self.post("/addition")(self.addition)
        self.post("/echo")(self.echo)
        self.websocket("/ws")(self.audio_websocket)

    async def status(self, health):
        return {"status": "ok"}
    
    async def addition(self, a: int, b: int):
        return {"result": a + b}
    
    async def echo(self, message: str):
        return {"message": message}
    
    async def audio_websocket(self, websocket: WebSocket):
        await websocket.accept()
        while True:
            data = await websocket.receive_bytes()

            await websocket.send_text('data received')
    
    def dashboard(self):
        return FileResponse("dashboard/index.html")
    
    def run(self):
        if self._development:
            uvicorn.run("main:jarvis", host="0.0.0.0", port=8000, reload=True)
        else:
            uvicorn.run("main:jarvis", host="0.0.0.0", port=8000)
    