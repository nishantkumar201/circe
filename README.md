# Erasmus

A local-first voice assistant with a full speech-to-text → LLM → text-to-speech pipeline, served remotely over Tailscale, with a live web dashboard.

## Status: Work in Progress

This is research/hobby code, not production-hardened. The orchestration/routing layer is currently being redesigned — see below.

## Architecture

- **STT**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (`base.en`, CUDA/float16) transcribes incoming audio
- **LLM**: Served locally via [Ollama](https://ollama.com/)
- **TTS**: [Kokoro](https://github.com/hexgrad/kokoro) synthesizes the response back to audio
- **Backend**: FastAPI, with WebSocket endpoints for both audio (`/ws/audio`) and text (`/ws/text`) interaction
- **Remote access**: Served over Tailscale, so the assistant can be reached securely from other devices without opening ports
- **Dashboard**: A live web UI showing health metrics, connected devices, a stock watchlist, and a real-time transcript feed of the conversation

## Orchestration layer (actively being redesigned)

The original router classified each incoming query by domain and depth using a single large prompt with hardcoded few-shot examples. That approach is being reworked to:

- Move deterministic rules (things that are _always_ true, like "system control queries are always simple") out of the prompt and into code, so only genuinely ambiguous cases reach the LLM
- Use structured output (JSON schema-constrained generation) instead of prompting the model to "output only JSON"
- Trim few-shot examples down to the cases that actually need them

This section will be filled in with the finalized design once the rework is complete.

### Working

- Full STT → LLM → TTS pipeline, functional end to end
- WebSocket-based audio and text interfaces
- Remote serving over Tailscale
- Dashboard with health metrics, device list, stock watchlist, and live transcript feed

### In progress

- Redesigning the query router/orchestration logic (see above)
- Escalation logic for when a query needs more than a direct LLM response (e.g. web search, document retrieval)
- Docstrings, error handling, and general code hardening

## Running it

Requires a CUDA-capable GPU, Ollama installed and models pulled locally, and Tailscale configured if you want remote access.

```
python main.py
```

The dashboard is served at `/` once the backend is running.

## Roadmap

- [ ] Finish reworked orchestration layer
- [ ] Tool-use escalation (web search, document retrieval)
- [ ] Persistent memory / conversation history across sessions
- [ ] Expand dashboard integrations
- [ ] Code cleanup and documentation pass
