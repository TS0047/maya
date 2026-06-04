# 🎙️ Maya — A Fully Offline Voice Assistant

> Talk to a local LLM. No cloud, no API keys, no data leaving your machine.

Maya is a **100% local, real-time voice assistant**. Speech recognition, language reasoning, and speech synthesis all run on your own hardware — making it a practical playground for **LLMs on constrained / edge devices**.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=flat-square&logo=ollama&logoColor=white)
![Whisper](https://img.shields.io/badge/faster--whisper-FFD21E?style=flat-square)
![Offline](https://img.shields.io/badge/100%25-Offline-success?style=flat-square)

---

## How It Works

```
🎤 Mic  →  Silero VAD  →  faster-whisper (STT)  →  Ollama LLM  →  Kokoro (TTS)  →  🔊 Speaker
          (detects        (transcribes              (generates       (speaks the
           speech)         to text)                  a reply)         response)
```

The pipeline listens continuously, detects when you start and stop speaking using **voice-activity detection**, transcribes your speech, sends it to a local LLM with conversational memory, and speaks the reply back — all without an internet connection.

---

## Features

- **Real-time voice-activity detection** — Silero VAD records only when you're actually speaking and stops on silence
- **Accurate offline transcription** — faster-whisper (`small`, int8) tuned for low latency on CPU
- **Local LLM reasoning** — Ollama (`mistral:7b`) with a witty assistant persona and 10-turn conversational memory
- **Natural offline speech** — Kokoro TTS (`af_bella` voice) for the response
- **Text mode fallback** — flip a flag to type instead of speak

---

## Project Structure

### `maya_v1/` — the working voice assistant
| File | Role |
|------|------|
| `listener.py` | Silero VAD + faster-whisper — captures mic audio and transcribes speech |
| `ollama_connection.py` | Main loop: STT → LLM → TTS with chat history (run this) |
| `ausdio_tts.py` | Kokoro TTS — synthesizes and plays the reply |
| `load.py` | Startup animation helper |

### `maya_v2/` — experimental agentic features
| File | Role |
|------|------|
| `langgraph_test.py` | LangGraph + Ollama agent workflow with tool calling |
| `apps_test.py` | Desktop app launching via AppOpener |
| `master.py` | LangChain prompt-pipeline demo |

---

## Setup

```bash
# 1. Install Ollama and pull the model
ollama pull mistral:7b

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run the assistant
python maya_v1/ollama_connection.py
```

> **Windows note:** `pyaudio` and `sounddevice` may need platform-specific wheels and working audio drivers. `faster-whisper` downloads its model on first run.

---

## Configuration

Key knobs live at the top of `maya_v1/listener.py`:

| Setting | Default | Notes |
|---------|---------|-------|
| `WHISPER_MODEL` | `small` | `tiny`/`base`/`small`/`medium`/`large-v3` |
| `WHISPER_DEVICE` | `cpu` | switch to `cuda` for GPU |
| `VAD_THRESHOLD` | `0.5` | higher = stricter speech detection |
| `SILENCE_DURATION` | `1.2s` | silence before recording stops |

Swap the LLM by changing `model = 'mistral:7b'` in `ollama_connection.py`.

---

## Roadmap

- [ ] Merge v2's LangGraph agent into the main voice loop (tool use by voice)
- [ ] Streaming TTS for lower response latency
- [ ] Wake-word detection
