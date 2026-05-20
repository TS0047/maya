from kokoro import KPipeline
import sounddevice as sd
import torch
def initiate():
    pipeline = KPipeline(lang_code='a')
    return pipeline 
def speak(text,pipeline):
    generator = pipeline(text, voice='af_bella', speed=1)
    for i, (gs, ps, audio) in enumerate(generator):
        sd.play(audio, samplerate=24000)
        sd.wait()
