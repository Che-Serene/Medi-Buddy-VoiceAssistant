import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from openai import OpenAI
from gtts import gTTS
import subprocess
import nest_asyncio; nest_asyncio.apply()
import asyncio
import edge_tts
import soundfile as sf

class Conversation:
    def __init__(self,
                 sample_rate=16000, 
                 frame_duration=30, 
                 vad_mode=1, 
                 threshold=5000, 
                 whisper_model_size='small',
                 openai_api_key=None,
                 tts_voice="ko-KR-SunHiNeural"):
        
        pass