import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from openai import OpenAI
import os
import nest_asyncio
nest_asyncio.apply()
import asyncio
import edge_tts
import soundfile as sf

MY_API_KEY = os.environ.get("OPENAPI_KEY")

sst_model = WhisperModel('tiny', compute_type='float32')
llm_model = OpenAI(api_key=MY_API_KEY).chat.completions

sample_rate = 16000
duration = 5

term = 0

async def make_tts(text):
    communicate = edge_tts.Communicate(text=text, voice="ko-KR-SunHiNeural")
    await communicate.save("output.wav")
    

while term < 3:
    print("녹음을 시작합니다")
    audio = sd.rec(int(duration*sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()

    print("녹음이 완료되었습니다. 음성 인식 중...")
    audio = audio.flatten().astype(np.float32) / 32768.0  # int16을 float32로 정규화
    segments, info = sst_model.transcribe(audio, language='ko')
    result = ''
    for segment in segments:
        result += segment.text
    print("음성 인식 결과:", result)
    re = llm_model.create(model='gpt-3.5-turbo', messages=[
    {"role": "system",
     "content": "너는 의료 지원 로봇이야. 친절하게 존댓말로 답변해줘. 이모티콘 금지. 3문장 내외로 간략하게 대답해",},
    {"role": "user", "content": result}]).choices[0].message.content
    asyncio.run(make_tts(re))
    data, sample_rate = sf.read('output.wav')
    sd.play(data, sample_rate)
    sd.wait()
    term+=1