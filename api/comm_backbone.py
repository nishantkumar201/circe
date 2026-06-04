import io
import subprocess
import uvicorn
import numpy as np
import soundfile as sf
import httpx
import time
import ollama
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from faster_whisper import WhisperModel
from kokoro import KPipeline

model = WhisperModel("base.en", device="cuda", compute_type="float16")
pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
client = ollama.AsyncClient()


class CommBackbone(FastAPI):
    def __init__(self):
        super().__init__()
        self._register_endpoints()
        self._development = True
        self.message = [
            {
                "role": "system",
                "content": (
                    "Your name is Jarvis. "
                    "You are a helpful assistant. You can understand and generate "
                    "natural language. You can also understand and generate audio. "
                    "You can perform various tasks such as answering questions, "
                    "providing information, and engaging in conversation. "
                    "You can also perform tasks such as summarizing text, translating "
                    "text, and creating text, you will have the ability to use tools soon."
                    "Do not use markdown, asterisks, bullet points, or any special formatting in your responses. "
                    "Do not use emojis, emoticons, or any other type of emoticons in your responses. "
                ),
            }
        ]

    def _start_ollama(self):
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(10):
            try:
                httpx.get("http://localhost:11434")
                print("Ollama ready")
                return
            except httpx.ConnectError:
                time.sleep(1)
        raise RuntimeError("Ollama failed to start")
    
    def _register_endpoints(self):
        self.get("/")(self.dashboard)
        self.get("/status")(self.status)
        self.post("/addition")(self.addition)
        self.post("/echo")(self.echo)
        self.websocket("/ws")(self.audio_websocket)

    async def _STT(self, websocket: WebSocket, chunks):
        text_chunks = []
        buf = io.BytesIO(b"".join(chunks))
        buf.seek(0)
        segments, _ = model.transcribe(buf)
        for segment in segments:
            print(segment.text)
            text_chunks.append(segment.text)
            await websocket.send_text(segment.text)
        full_text = " ".join(text_chunks)
        return full_text
    
    async def _LLM(self, text):
        self.message.append({"role": "user", "content": text})
        response = await client.chat(model = "llama3.2", messages = self.message)
        assistant_content = response.message.content
        self.message.append({"role": "assistant", "content": assistant_content})
        return assistant_content
    
    async def _TTS(self, websocket: WebSocket, full_text):
        # print("full_text", full_text)
        audio_chunks_list = []
        if full_text:
            generator = pipeline(full_text, voice="bm_george", speed=1.25)

            for _, _, audio in generator:
                audio_chunks_list.append(audio)
            full_audio = np.concatenate(audio_chunks_list)
            # sf.write("output.wav", full_audio, 24000)
            # print("Audio saved to output.wav")

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
                        response = await self._LLM(text)
                        await self._TTS(websocket, response)
                        break
        except Exception as e:
            print(f"Disconnected: {e}")

    def dashboard(self):
        return FileResponse("dashboard/index.html")

    def run(self):
        if self._development:
            uvicorn.run("main:jarvis", host="0.0.0.0", port=8000, reload=True)
        else:
            uvicorn.run("main:jarvis", host="0.0.0.0", port=8000)