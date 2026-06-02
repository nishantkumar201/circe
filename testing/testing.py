import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from pathlib import Path
import io
from faster_whisper import WhisperModel

app = FastAPI()
HERE = Path(__file__).parent

model = WhisperModel("base.en", device="cpu")


@app.get("/")
def dashboard():
    return FileResponse(HERE / "testing.html")


@app.websocket("/ws")
async def audio_websocket(websocket: WebSocket):
    chunks = []
    await websocket.accept()
    print("Client connected")
    try:
        while True:
            data = await websocket.receive()
            if "bytes" in data:
                chunks.append(data["bytes"])
                print("chunk received")
            elif "text" in data:
                if data["text"] == "End of Recording":
                    print("End of recording")
                    buf = io.BytesIO(b"".join(chunks))
                    segments, _ = model.transcribe(buf)
                    for segment in segments:
                        print(segment.text)
                        await websocket.send_text(segment.text)
                    break

    except Exception as e:
        print(f"Disconnected: {e}")


if __name__ == "__main__":
    uvicorn.run("testing:app", host="0.0.0.0", port=8000, reload=True)
