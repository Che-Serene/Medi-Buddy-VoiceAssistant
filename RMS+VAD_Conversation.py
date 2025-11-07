import pyaudio
import webrtcvad
import collections
import numpy as np
from faster_whisper import WhisperModel
from openai import OpenAI
import asyncio
import edge_tts
import sounddevice as sd
import soundfile as sf
from time import sleep
import os

sample_rate = 16000
frame_duration = 30
frame_size = int(sample_rate * frame_duration / 1000)
vad = webrtcvad.Vad(1)
term = 0

sst_model = WhisperModel('tiny', compute_type='float32')
MY_API_KEY = os.environ.get("OPENAPI_KEY")

llm_model = llm_model = OpenAI(api_key=MY_API_KEY).chat.completions
def is_loud_enough(frame, threshold=5000):
    pcm_data = np.frombuffer(frame, dtype=np.int16)
    if pcm_data.size == 0:
        return False
    pcm_data = pcm_data.astype(np.float32)
    if np.any(np.isnan(pcm_data)) or np.any(np.isinf(pcm_data)):
        return False
    rms = np.sqrt(np.mean(pcm_data**2))
    return rms > threshold

def listen_and_record():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=frame_size)

    ring_buffer = collections.deque(maxlen=10)
    triggered = False
    voiced_frames = []

    print("계속 대기 중... 음성이 들리면 녹음 시작")

    while True:
        frame = stream.read(frame_size, exception_on_overflow=False)
        is_speech = vad.is_speech(frame, sample_rate) and is_loud_enough(frame)
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.7 * ring_buffer.maxlen :
                triggered = True
                print("음성 감지: 녹음 시작")
                voiced_frames.extend([f for f, s in ring_buffer])
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > 0.7 * ring_buffer.maxlen:
                print("음성 종료: 녹음 중지")
                break

    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_data = b"".join(voiced_frames)
    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
    return audio_np
async def make_tts(text):
    communicate = edge_tts.Communicate(text=text, voice="ko-KR-SunHiNeural")
    await communicate.save("output.wav")

# listen_and_record()가 호출되면 계속 대기하다 음성 감지 시 녹음 시작 -> 음성 끝나면 녹음 종료 후 데이터 반환
while term<3:
    audio = listen_and_record()

    segments, info = sst_model.transcribe(audio, language='ko')
    result = ''
    for segment in segments:
        result += segment.text
    print("음성 인식 결과:", result)

    re = llm_model.create(model='gpt-3.5-turbo', messages=[
    {"role": "system",
     "content": "당신은 의료 지원 로봇 'Medi-Buddy'입니다. 3문장 내외 존댓말로 친근하게 답변합니다. 이모티콘 금지.",},
    {"role": "user", "content": result}]).choices[0].message.content
    print(re)
    asyncio.run(make_tts(re))
    data, sample_rate1 = sf.read('output.wav')
    sleep(0.01)
    sd.play(data, sample_rate1)
    sd.wait()
    term+=1