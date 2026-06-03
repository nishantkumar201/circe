import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from pathlib import Path
import io
from faster_whisper import WhisperModel
from kokoro import KPipeline
import numpy as np
import soundfile as sf

app = FastAPI()
HERE = Path(__file__).parent

model = WhisperModel("base.en", device="cpu")
pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")


@app.get("/")
def dashboard():
    return FileResponse(HERE / "testing.html")


@app.websocket("/ws")
async def audio_websocket(websocket: WebSocket):
    chunks = []
    text_chunks = []
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
                    audio_in = io.BytesIO(b"".join(chunks))
                    segments, _ = model.transcribe(audio_in)
                    for segment in segments:
                        print(segment.text)
                        text_chunks.append(segment.text)

                    await websocket.send_text(segment.text)

                    full_text = " ".join(text_chunks)

                    print("full_text", full_text)
                    audio_chunks_list = []
                    if full_text:
                        generator = pipeline(full_text, voice="af_heart", speed=1.0)

                        for _, _, audio in generator:
                            audio_chunks_list.append(audio)
                        full_audio = np.concatenate(audio_chunks_list)
                        # sf.write("output.wav", full_audio, 24000)
                        # print("Audio saved to output.wav")

                        audio_out = io.BytesIO()
                        sf.write(audio_out, full_audio, 24000, format="WAV")
                        audio_out.seek(0)
                        await websocket.send_bytes(audio_out.read())
                    break

    except Exception as e:
        print(f"Disconnected: {e}")


if __name__ == "__main__":
    uvicorn.run("testing:app", host="0.0.0.0", port=8000, reload=True)
