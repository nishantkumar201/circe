const menuBtn = document.getElementById("menu-btn");
const sidebar = document.querySelector("aside");
const overlay = document.getElementById("sidebar-overlay");
const record = document.getElementById("record-btn");
const currentTime = document.getElementById("current-time");
const textInput = document.getElementById("text-input");

let recording = false;
let mediaRecorder = null;
let chunks = [];
let socket = null;

menuBtn.onclick = () => {
  sidebar.classList.toggle("open");
  overlay.classList.toggle("open");
};

overlay.onclick = () => {
  sidebar.classList.remove("open");
  overlay.classList.remove("open");
};

updateClock();
setInterval(updateClock, 1000);

record.onclick = async () => {
  if (!recording) {
    await startRecording();
    recording = true;
  } else if (recording) {
    stopRecording();
    recording = false;
  }
};
async function startRecording() {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    let wsProtocol;
    if (location.protocol == "https:") {
      wsProtocol = "wss:";
    } else {
      wsProtocol = "ws:";
    }
    const socket = new WebSocket(`${wsProtocol}//${location.host}/ws/audio`);
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
          socket.send("End of Recording");
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
        const url = URL.createObjectURL(e.data);
        const audio = new Audio(url);
        audio.play();
        audio.onended = () => {
          URL.revokeObjectURL(url);
        };
        console.log("Server is doing audio transcription");
      } else if (typeof e.data === "string") {
        if (e.data.startsWith("USER: ")) {
          appendMessage("user", e.data.slice(6));
        } else if (e.data.startsWith("ASSISTANT: ")) {
          appendMessage("erasmus", e.data.slice(11));
        }
      }
    };
  } else {
    console.log("getUserMedia not supported.");
  }
}

document.getElementById("send-btn").onclick = () => {
  try {
    const text = textInput.value.trim();
    if (!text) return;
    let wsProtocol;
    if (location.protocol == "https:") {
      wsProtocol = "wss:";
    } else {
      wsProtocol = "ws:";
    }
    const webSocket = new WebSocket(`${wsProtocol}//${location.host}/ws/text`);

    webSocket.onopen = () => {
      appendMessage("user", text);
      webSocket.send(text);
      textInput.value = "";
    };

    webSocket.onmessage = (e) => {
      if (e.data.startsWith("ASSISTANT: ")) {
        appendMessage("erasmus", e.data.slice(11));
      }
    };
  } catch (error) {
    console.error("Error:", error);
  }
};

function appendMessage(type, text) {
  const feed = document.getElementById("transcript-feed");
  const div = document.createElement("div");
  div.classList.add("message", type);
  div.textContent = text;
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

document.getElementById("text-input").onkeydown = (e) => {
  if (e.key === "Enter") document.getElementById("send-btn").onclick();
};

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
