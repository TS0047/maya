import LLM.maya_v1.ausdio_tts as ausdio_tts
import ollama
from datetime import date
import LLM.maya_v1.listener as listener
import LLM.maya_v1.load as load

day = date.today()
client = ollama.Client()
model = 'mistral:7b'
lol = ausdio_tts.initiate()
chat = {}
chat["chat_history"] = []

voice_needed = True
need_load = True

if voice_needed:
    vad,whisper = listener.load_models()

system_prompt = (
    f"Today's date: {day}."
    "Your name is Maya. You are the personal human assisstant of phoenix."
    "Keep responses witty and very humorous as you are a smart women."
    "No emojis or newlines. Your response is for TTS."
)


if need_load:
    load.load_animation()
else:
    print("\033[H\033[J", end="")

ausdio_tts.speak("Initializing maya",lol)
print("Initializing maya")
try:
    while True:
        if voice_needed:
            prompt = listener.listen_loop(vad_model=vad,whisper_model=whisper)
            print("User : "+prompt)
        else:
            prompt = input("User : ")
        if prompt != "quit" or prompt !="demolish yourself" :
            chat["chat_history"].append("User : "+prompt)
            response = client.generate(model=model,system=system_prompt,prompt="\n".join(chat["chat_history"][-10:]) ).response
            chat["chat_history"].append("maya : "+response)
            print("maya : ",response)
            ausdio_tts.speak(response,lol)
        else:
            print("maya : self destructing !")
            ausdio_tts.speak("self destructing !",lol)
            break;
except(KeyboardInterrupt):
    print("\nmaya : self destructing !")
    ausdio_tts.speak("self destructing !",lol)

