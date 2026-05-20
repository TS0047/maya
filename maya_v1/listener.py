import numpy as np
import pyaudio
import torch
import time
from faster_whisper import WhisperModel

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
SAMPLE_RATE       = 16000
CHUNK_SIZE        = 512          # must be 512 for Silero VAD
SILENCE_DURATION  = 1.2          # seconds of silence before we stop recording
MIN_SPEECH_CHUNKS = 8            # ignore very short sounds (< ~250ms)
VAD_THRESHOLD     = 0.5          # 0.0–1.0, higher = stricter
WHISPER_MODEL     = "small"      # tiny / base / small / medium / large-v3
WHISPER_DEVICE    = "cpu"        # "cpu" or "cuda"
WHISPER_COMPUTE   = "int8"       # int8 (cpu) | float16 (cuda)
LANGUAGE          = "en"         # set to None for auto-detect


# ─────────────────────────────────────────
#  LOAD MODELS
# ─────────────────────────────────────────
def load_models():
    vad_model, utils = torch.hub.load(
        repo_or_dir="snakers4/silero-vad",
        model="silero_vad",
        force_reload=False,
        onnx=False,
    )
    vad_model.eval()

    whisper_model = WhisperModel(
        WHISPER_MODEL,
        device=WHISPER_DEVICE,
        compute_type=WHISPER_COMPUTE,
    )

    return vad_model, whisper_model


# ─────────────────────────────────────────
#  VAD HELPER
# ─────────────────────────────────────────
def is_speech(chunk: bytes, vad_model) -> bool:
    """Returns True if Silero VAD detects speech in this 512-sample chunk."""
    audio_np = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
    audio_tensor = torch.from_numpy(audio_np)
    with torch.no_grad():
        confidence = vad_model(audio_tensor, SAMPLE_RATE).item()
    return confidence >= VAD_THRESHOLD


# ─────────────────────────────────────────
#  RECORD UNTIL SILENCE
# ─────────────────────────────────────────
def record_utterance(vad_model) -> np.ndarray | None:
    """
    Opens the mic, waits for speech to start,
    then records until silence is detected.
    Returns a float32 numpy array at 16kHz, or None if nothing was captured.
    """
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
    )

    print("🎤 Listening... (speak now)")

    frames          = []
    silent_chunks   = 0
    speech_chunks   = 0
    recording       = False
    max_silent      = int(SILENCE_DURATION * SAMPLE_RATE / CHUNK_SIZE)

    try:
        while True:
            chunk = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            speech = is_speech(chunk, vad_model)

            if speech:
                silent_chunks = 0
                speech_chunks += 1

                if not recording:
                    recording = True
                    print("● Recording...")

                frames.append(chunk)

            else:
                if recording:
                    frames.append(chunk)   # include trailing silence
                    silent_chunks += 1

                    if silent_chunks >= max_silent:
                        print("■ Silence detected — processing...\n")
                        break

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    # Discard if too short (background noise blip)
    if speech_chunks < MIN_SPEECH_CHUNKS:
        print("[!] Too short, ignoring.\n")
        return None

    audio_np = np.frombuffer(b"".join(frames), dtype=np.int16).astype(np.float32)
    audio_np /= 32768.0          # normalise to [-1, 1]
    return audio_np


# ─────────────────────────────────────────
#  TRANSCRIBE
# ─────────────────────────────────────────
user_context = "the user's name is phoenix. the name of the LLM is maya . he is talking to maya , demolish yourself"
def transcribe(audio: np.ndarray, whisper_model: WhisperModel) -> str:
    segments, info = whisper_model.transcribe(
        audio,
        initial_prompt=user_context,
        language=LANGUAGE,
        beam_size=5,
        best_of=5,
        temperature=0.0,              # deterministic
        vad_filter=True,              # second-pass VAD inside Whisper
        vad_parameters=dict(
            min_silence_duration_ms=300,
            speech_pad_ms=400,
        ),
        condition_on_previous_text=True,
        word_timestamps=False,
    )

    text = " ".join(seg.text.strip() for seg in segments)
    return text.strip()


# ─────────────────────────────────────────
#  MAIN LOOP  (plug Kokoro in here)
# ─────────────────────────────────────────
def listen_loop(vad_model, whisper_model):
    """
    Continuously listens and calls on_transcript_callback(text)
    whenever the user finishes speaking.

    Usage:
        def handle(text):
            print("User said:", text)
            # → send to your LLM → Kokoro TTS

        listen_loop(handle)
    """

    while True:
        audio = record_utterance(vad_model)

        if audio is None:
            continue

        t0   = time.time()
        text = transcribe(audio, whisper_model)
        dt   = time.time() - t0

        if text:
            
            return text
        else:
            print("[!] Empty transcript, skipping.\n")
