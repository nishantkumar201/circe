const record = document.getElementById("record-btn");
const currentTime = document.getElementById("current-time");

let recording = false;
let mediaRecorder = null;
let chunks = [];

updateClock();
setInterval(updateClock, 1000);

record.onclick = async () => {
  if (!recording) {
    await startRecording();
    recording = true;
  } else if (recording) {
    stopRecording();
    recording = false;
  } else {
    console.log("Error starting recording.");
  }
};

async function startRecording() {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    const socket = new WebSocket("REDACTED_HOST");
    console.log("getUserMedia supported.");
    socket.onopen = async () => {
      console.log("Connected to WebSocket server.");
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
          video: false,
        });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.onstop = () => {
          mediaRecorder.stream.getTracks().forEach((t) => t.stop());
        };

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            chunks.push(e.data);
            socket.send(e.data);
            console.log("chunks", e.data.size);
          }
        };

        mediaRecorder.start(1000);
        console.log("Recording...");
        record.classList.add("recording");
      } catch (err) {
        console.error("Mic error:", err);
        recording = false;
        record.classList.remove("recording");
      }
    };
    socket.onmessage = async (e) => {
      if (e.data instanceof Blob) {
        const arrayBuf = await e.data.arrayBuffer();
        console.log("Server is doing audio transcription");
        if (!audioCtx) {
          audioCtx = new AudioContext();
        }
        const audioBuffer = await audioCtx.decodeAudioData(arrayBuf);
        const source = audioCtx.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioCtx.destination);
        source.start();
      } else if (typeof e.data === "string") {
        console.log("server says", e.data);
      }
    };
  } else {
    console.log("getUserMedia not supported.");
  }
}

function stopRecording() {
  mediaRecorder.stop();
  console.log("Recording stopped.");
  record.classList.remove("recording");
}

function updateClock() {
  currentTime.textContent = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}
