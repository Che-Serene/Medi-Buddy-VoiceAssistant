import speech_recognition as sr
import pyaudio

r = sr.Recognizer()
r.pause_threshold = 1
r.dynamic_energy_adjustment = True

with sr.Microphone() as source:
    print('Speack Anything :')
    audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language= 'ko-KR')
        print('You said : {}'.format(text))
    except:
        print('Sirry could not recignize your voice')
