const record = document.getElementById("record-btn");
const currentTime = document.getElementById("current-time");

let recording = false;
let mediaRecorder = null;
let chunks = [];
let audioContext = null;

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
      socket.binaryType = "arraybuffer";
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
    socket.onmessage = (e) => {
      if (typeof e.data == "string") {
        console.log("server says", e.data);
      } else if (e.data instanceof ArrayBuffer) {
        console.log("Incoming audio chunk");
        try {
          if (!audioContext) {
            audioContext = new (
              window.AudioContext || window.webkitAudioContext
            )();
          }
          const float32Data = new Float32Array(e.data);
          const sampleRate = 24000;
          const audioBuffer = audioContext.createBuffer(
            1,
            float32Data.length,
            sampleRate,
          );
          audioBuffer.getChannelData(0).set(float32Data);

          const audioSource = audioContext.createBufferSource();
          audioSource.buffer = audioBuffer;
          audioSource.connect(audioContext.destination);
          audioSource.start(0);
        } catch (err) {
          console.error("Error processing audio chunk:", err);
        }
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
