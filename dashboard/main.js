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
let firstToken = true;
let currentAssistantDiv = null;
let currentAssistantText = "";

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
    firstToken = true;
    currentAssistantDiv = null;
    currentAssistantText = "";

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
    socket = new WebSocket(`${wsProtocol}//${location.host}/ws/audio`);
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
        console.log("Server is finished doing audio transcription");
      } else if (typeof e.data === "string") {
        if (e.data.startsWith("USER: ")) {
          appendMessage("user", e.data.slice(6));
        } else {
          const event = JSON.parse(e.data);
          if (event.type === "token") {
            if (firstToken === true) {
              const thinkingMessage = document.querySelector(".thinking-message");
              if (thinkingMessage) thinkingMessage.remove();
              currentAssistantDiv = appendMessage("circe", "");
              firstToken = false;
            }
            currentAssistantText += event.content;
            const span = document.createElement("span");
            span.classList.add("token-span");
            span.textContent = event.content;
            currentAssistantDiv.appendChild(span);
            scrollToBottom(currentAssistantDiv);
          } else if (event.type === "end") {
            currentAssistantDiv.innerHTML = marked.parse(currentAssistantText);
          }
        }
      }
    };
  } else {
    console.log("getUserMedia not supported.");
  }
}

document.getElementById("send-btn").onclick = () => {
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
    appendMessage("circe", "Thinking...");
    firstToken = true;
    currentAssistantText = "";
    currentAssistantDiv = null;
  };

  webSocket.onmessage = (e) => {
    const event = JSON.parse(e.data);

    if (event.type === "token") {
      if (firstToken === true) {
        const thinkingMessage = document.querySelector(".thinking-message");
        if (thinkingMessage) thinkingMessage.remove();
        currentAssistantDiv = appendMessage("circe", "");
        firstToken = false;
      }
      currentAssistantText += event.content;
      const span = document.createElement("span");
      span.classList.add("token-span");
      span.textContent = event.content;
      currentAssistantDiv.appendChild(span);
      scrollToBottom(currentAssistantDiv);
    } else if (event.type === "end") {
      currentAssistantDiv.innerHTML = marked.parse(currentAssistantText);
    }
  };

  webSocket.onerror = (err) => {
    console.error("WebSocket error:", err);
  };
};

function appendMessage(type, text) {
  const feed = document.getElementById("transcript-feed");
  const div = document.createElement("div");
  div.classList.add("message", type);

  if (text === "Thinking...") {
    div.classList.add("thinking-message");
    div.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
  } else if (type === "circe" && typeof marked !== "undefined") {
    div.innerHTML = marked.parse(text);
  } else {
    div.textContent = text;
  }

  feed.appendChild(div);
  scrollToBottom(div);
  return div;
}

function scrollToBottom(latestEl) {
  requestAnimationFrame(() => {
    const feed = document.getElementById("transcript-feed");

    feed.scrollTo({
      top: feed.scrollHeight,
      behavior: "smooth",
    });

    if (latestEl && latestEl.scrollIntoView) {
      latestEl.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  });
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