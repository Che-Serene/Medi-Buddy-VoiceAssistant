# About
- sst.py: 사용자의 음성을 탐지하여 자동으로 녹음을 시작 및 중단
- tts.py: 비동기로 Edge TTS를 이용하여 오디오 파일을 만들고 재생

# How to start
1. 리포지토리 클론
```bash
git clone https://github.com/Che-Serene/Medi-Buddy-VoiceAssistant.git
```
2. 가상환경 실행
```bash
python3 -m venv [가상환경이름]
source [가상환경이름]/bin/activate
```
3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```
4. (필요 시) OpenAI API KEY 환경 변수 설정
```bash
export OPENAPI_KEY=[YOUR_OPENAI_API_KEY]
```
# 예시 코드
## SST
```python
from modules.sst import RMS_VAD
rv = RMS_VAD()
rv.run()
```
## TTS
```python
from modules.tts import TTS
tts = TTS()
tts.make_and_play("테스트 문자열")
```
## 음성 기반 챗봇 구현
```python
from openai import OpenAI
from modules.sst import RMS_VAD
from modules.tts import TTS
import os

MY_API_KEY = os.environ.get("OPENAPI_KEY")
llm_model = OpenAI(api_key=MY_API_KEY).chat.completions
rv = RMS_VAD()
tts = TTS()

for _ in range(3):
    result = rv.run()
    re = llm_model.create(model='gpt-3.5-turbo', messages=[
    {"role": "system",
        "content": "당신은 의료 지원 로봇 'Medi-Buddy'입니다. 3문장 내외 존댓말로 친근하게 답변합니다.",},
    {"role": "user", "content": result}]).choices[0].message.content
    print(re)
    tts.make_and_play(re)
```

## Directory
.        
├── **main.py**      
├── modules         
│   ├── sst.py         
│   └── tts.py           
├── requirements.txt               
└──  RMS_threshold_test.py      
