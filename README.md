# Maya Assistant

This folder contains the Maya assistant prototypes:

- `maya_v1/` — voice assistant stack with microphone input, Whisper transcription, Ollama chat, and TTS output.
- `maya_v2/` — test scripts featuring desktop app tooling and LangGraph-based agent workflows.

## Installation

From the repo root or the `maya/` folder, install dependencies:

```powershell
pip install -r maya/requirements.txt
```

> On Windows, `pyaudio` and `sounddevice` may need platform-specific wheels or system audio drivers.

## Files

### `maya_v1/`
- `ausdio_tts.py` — initializes Kokoro TTS and plays audio with `sounddevice`.
- `listener.py` — loads Silero VAD and Faster Whisper to capture microphone audio and transcribe speech.
- `load.py` — simple startup animation helper.
- `ollama_connection.py` — example Ollama client usage for generating assistant responses.

### `maya_v2/`
- `apps_test.py` — basic AppOpener sample.
- `langgraph_test.py` — LangGraph + Ollama planning/assistant tool integration.
- `master.py` — simple demo `load_animation` runnable script.

## Usage

### Run the v1 assistant loop

```powershell
python maya/maya_v1/ollama_connection.py
```

### Run the v2 LangGraph demo

```powershell
python maya/maya_v2/langgraph_test.py
```

## Notes

- `ollama` usage requires an Ollama server or local Ollama runtime.
- `kokoro` supports offline TTS but may require valid voice models and audio device access.
- `faster-whisper` and `torch` are used for speech transcription.
- `AppOpener` is used in the `maya_v2` test scripts to open local desktop applications.
