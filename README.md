# CIRCE

**A private, local-first personal AI assistant.**

Circe is an ongoing experiment in building a personal AI system that runs primarily on local hardware. The goal is to keep speech, inference, personal data, retrieval, and automation local where possible, while allowing individual models and components to be swapped, extended, or selectively escalated as the system evolves.

## Status: Work in Progress

Circe is currently research/hobby code, not a production-hardened application.

The core voice pipeline is functional end to end. Current development is focused on redesigning the orchestration layer that will eventually handle routing, tool use, retrieval, and model selection.

## Current Architecture

```text
Microphone
    ↓
MediaRecorder
    ↓
WebSocket
    ↓
FastAPI
    ↓
faster-whisper
    ↓
Text
    ↓
Circe Orchestrator
    ↓
Ollama / Local LLM
    ↓
Streamed Response
    ↓
Kokoro
    ↓
WAV
    ↓
WebSocket
    ↓
Browser Audio
```

### Components

- **STT:** [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (`base.en`, CUDA/float16) transcribes incoming audio.
- **LLM:** Local language models are served through [Ollama](https://ollama.com/).
- **TTS:** [Kokoro](https://github.com/hexgrad/kokoro) synthesizes responses back into speech.
- **Backend:** FastAPI provides WebSocket interfaces for both audio (`/ws/audio`) and text (`/ws/text`).
- **Remote access:** Circe is served over Tailscale, allowing it to be accessed privately from other devices without exposing the backend directly to the public internet.
- **Dashboard:** A web interface provides the conversation feed alongside areas for health metrics, connected devices, and a stock watchlist.

## Orchestration Layer

The orchestration layer sits between Circe's interfaces and its models. Its purpose is to eventually decide what information, tools, and models are needed to handle a request rather than sending every query directly to a single LLM.

The original router classified incoming queries by domain and depth using a large prompt with hardcoded few-shot examples. That design is currently being reworked to:

- Move deterministic routing rules out of the LLM prompt and into code.
- Use structured output instead of relying on prompts requesting raw JSON.
- Reserve LLM classification for genuinely ambiguous requests.
- Support future escalation to tools, retrieval, and other models without coupling them directly to the interface layer.

The implementation is still evolving as the rest of Circe's capabilities are developed.

## Working

- End-to-end STT → LLM → TTS voice pipeline
- Streaming local LLM responses
- Audio and text WebSocket interfaces
- Browser-based microphone input and audio playback
- Remote access over Tailscale
- Responsive web dashboard and live conversation transcript

## In Progress

- Redesigning the query router/orchestration logic
- Structured routing output
- Escalation for requests requiring tools or external information
- Error handling and general code hardening
- Expanding dashboard data integrations

## Running Circe

Circe currently requires:

- Python and the project's dependencies
- A CUDA-capable GPU for the current faster-whisper configuration
- Ollama with the required model(s) pulled locally
- Tailscale if remote access is desired

Run:

```bash
python main.py
```

The dashboard is served at `/` once the backend is running.

## Roadmap

- [ ] Finish the reworked orchestration layer
- [ ] Add tool-use escalation
- [ ] Add document retrieval / RAG
- [ ] Add persistent conversation history and memory
- [ ] Expand personal-data and dashboard integrations
- [ ] Add model routing and optional cloud escalation
- [ ] Continue improving voice interaction
- [ ] Code cleanup, testing, and documentation

## Project Direction

Circe is intended to grow beyond a voice interface for a local LLM. The longer-term goal is a modular personal AI system that can combine local models, private data, retrieval, tools, and device integrations while keeping the user in control of what information leaves their own hardware.
