from fastapi import FastAPI
import uvicorn
from fastapi.responses import FileResponse


class CommBackbone(FastAPI):
    def __init__(self):
        super().__init__()
        self._register_endpoints()
        
    def _register_endpoints(self):
        self.get("/")(self.dashboard)
        self.get("/status")(self.status)
        self.post("/addition")(self.addition)
        self.post("/echo")(self.echo)

    async def status(self, health):
        return {"status": "ok"}
    
    async def addition(self, a: int, b: int):
        return {"result": a + b}
    
    async def echo(self, message: str):
        return {"message": message}
    
    def dashboard(self):
        return FileResponse("dashboard/index.html")
    
    def run(self):
        uvicorn.run(self, host="0.0.0.0", port=8000)
    