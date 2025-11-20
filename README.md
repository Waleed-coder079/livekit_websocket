# LiveKit Agent + WebSocket LLM (Windows)

A minimal LiveKit Python agent that:
- Uses Deepgram for STT, ElevenLabs for TTS, and Silero for VAD.
- Sends user text to a custom WebSocket LLM and streams the reply back.
- Includes a tiny echo WebSocket server (`server.py`) for local testing.

## Requirements
- Python 3.10+ (recommended 3.11)
- A LiveKit Cloud or self-hosted server (URL, API key, secret)
- API keys:
  - Deepgram: `DEEPGRAM_API_KEY`
  - ElevenLabs: `ELEVENLABS_API_KEY` (plus optional voice/model)

## Quickstart (PowerShell)
```powershell
# From repo root
python -m venv .\venv
.\venv\Scripts\Activate.ps1
pip install -r .\requirements.txt
```

Create a `.env` file in the repo root:
```env
# LiveKit connection (required to run the agent worker)
LIVEKIT_URL=ws://your-livekit-host:7880
LIVEKIT_API_KEY=lk_api_key
LIVEKIT_API_SECRET=lk_api_secret

# Speech services
DEEPGRAM_API_KEY=dg_api_key
ELEVENLABS_API_KEY=el_api_key
ELEVENLABS_VOICE_ID=Rachel
ELEVENLABS_TTS_MODEL=eleven_multilingual_v2
ELEVENLABS_STREAMING_LATENCY=0

# Local WebSocket LLM (you can use the included echo server)
WS_SERVER_URL=ws://127.0.0.1:8080/ws
```

## Run the demo WebSocket server (optional)
This is a simple echo server the agent can talk to locally.
```powershell
.\venv\Scripts\Activate.ps1
python .\server.py
```
It listens on `ws://127.0.0.1:8080/ws`.

## Run the agent
You can run the agent script directly:
```powershell
.\venv\Scripts\Activate.ps1
python .\main.py
```

Or use the helper PowerShell script (passes an optional mode argument, defaults to `console`):
```powershell
# Modes: console | dev | start
.\start-agent.ps1 -Mode console
```

When the worker connects to your LiveKit server, you can invite it into a room.

## Files
- `main.py` — Agent entrypoint; wires STT/TTS/VAD and the WebSocket LLM.
- `server.py` — Minimal echo WebSocket server for local testing.
- `requirements.txt` — Python dependencies.
- `start-agent.ps1` — Convenience script to run the agent on Windows.

## Troubleshooting
- If PyTorch (used by Silero) is slow to install on Windows, ensure you are using a supported Python version and allow some time for wheel downloads.
- Ensure your `.env` values are correct; missing keys commonly cause runtime errors from STT/TTS providers or the LiveKit connector.
- If you don’t have LiveKit credentials yet, comment out the agent run and just test the echo server first.
