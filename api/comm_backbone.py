import io
import uvicorn
import numpy as np
import soundfile as sf
import re
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from faster_whisper import WhisperModel
from kokoro import KPipeline

import api.LLM as LLM

model = WhisperModel("base.en", device="cuda", compute_type="float16")
pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
llm = LLM.LLM()


class CommBackbone(FastAPI):
    def __init__(self):
        super().__init__()
        self._register_endpoints()
        self._development = False

    def _register_endpoints(self):
        self.get("/")(self.dashboard)
        self.get("/status")(self.status)
        self.post("/addition")(self.addition)
        self.post("/echo")(self.echo)
        self.websocket("/ws/audio")(self.audio_websocket)
        self.websocket("/ws/text")(self.text_websocket)

    async def _STT(self, websocket: WebSocket, chunks):
        text_chunks = []
        buf = io.BytesIO(b"".join(chunks))
        buf.seek(0)
        segments, _ = model.transcribe(buf)
        for segment in segments:
            print(segment.text)
            text_chunks.append(segment.text)
            await websocket.send_text(f"USER: {segment.text}")
        full_text = " ".join(text_chunks)
        return full_text

    async def _TTS(self, websocket: WebSocket, full_text):
        cleaned_text = re.sub(r'[^a-zA-Z0-9\s\.\,\!\?]', '', full_text)
        audio_chunks_list = []
        if full_text:
            generator = pipeline(cleaned_text, voice="bf_alice", speed=1.25)

            for _, _, audio in generator:
                audio_chunks_list.append(audio)
            full_audio = np.concatenate(audio_chunks_list)

            audio_out = io.BytesIO()
            sf.write(audio_out, full_audio, 24000, format="WAV")
            audio_out.seek(0)
            await websocket.send_bytes(audio_out.read())

    async def status(self):
        return {"status": "ok"}

    async def addition(self, a: int, b: int):
        return {"result": a + b}

    async def echo(self, message: str):
        return {"message": message}

    async def audio_websocket(self, websocket: WebSocket):
        chunks = []

        await websocket.accept()
        print("Client connected")
        try:
            while True:
                data = await websocket.receive()
                if "bytes" in data:
                    chunks.append(data["bytes"])
                elif "text" in data:
                    if data["text"] == "End of Recording":
                        text = await self._STT(websocket, chunks)
                        response = await llm.orchestration_layer(text)
                        await websocket.send_text(f"ASSISTANT: {response}")
                        await self._TTS(websocket, response)
                    else:
                        await websocket.send_text(data["text"])
        except Exception as e:
            print(f"Disconnected: {e}")

    async def text_websocket(self, websocket: WebSocket):
        await websocket.accept()
        print("Client connected")

        try:
            while True:
                data = await websocket.receive_text()
                response = await llm.orchestration_layer(data)
                await websocket.send_text(f"ASSISTANT: {response}")
        except Exception as e:
            print(f"Disconnected: {e}")

    def dashboard(self):
        return FileResponse("dashboard/index.html")

    def run(self):
        if self._development:
            uvicorn.run("main:jarvis", host="0.0.0.0", port=8000, reload=True)
        else:
            uvicorn.run("main:jarvis", host="0.0.0.0", port=8000)