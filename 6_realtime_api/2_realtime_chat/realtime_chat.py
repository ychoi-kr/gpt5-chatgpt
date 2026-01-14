import asyncio
import websockets
import pyaudio
import base64
import json
import os

# OpenAI API 키 가져오기 (환경 변수에서)
API_KEY = os.environ.get("OPENAI_API_KEY")

# WebSocket 연결 대상 URL과 헤더 정보
WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "OpenAI-Beta": "realtime=v1"
}

# 음성 데이터를 Base64에서 PCM16으로 변환
def base64_to_pcm16(base64_audio: str) -> bytes:
    return base64.b64decode(base64_audio)

# 음성 입력 태스크
async def send_audio(websocket, stream, chunk_size: int):
     # 마이크에서 음성을 읽어오는 함수
    def read_audio_block():
        try:
            return stream.read(chunk_size, exception_on_overflow=False)
        except Exception as e:
            print(e)
            return None

    # 음성 입력 태스크 루프
    while True:
        # 마이크에서 음성 읽기
        audio_data = await asyncio.get_event_loop().run_in_executor(None, read_audio_block)
        if audio_data is None:
            continue

        # 음성 데이터를 PCM16에서 Base64로 변환
        base64_audio = base64.b64encode(audio_data).decode("utf-8")

        # 송신용 이벤트 데이터 생성
        audio_event = {
            "type": "input_audio_buffer.append",
            "audio": base64_audio
        }

        # 서버에 WebSocket 메시지로 전송
        await websocket.send(json.dumps(audio_event))
        await asyncio.sleep(0)

# 음성 출력 태스크
async def receive_audio(websocket, output_stream):
    loop = asyncio.get_event_loop()

    # 음성 출력 태스크 루프
    while True:
        # 서버로부터 WebSocket 메시지 수신
        response = await websocket.recv()
        response_data = json.loads(response)

        # 텍스트 표시
        if response_data.get("type") == "response.audio_transcript.delta":
            print(response_data.get("delta", ""), end="", flush=True)
        elif response_data.get("type") == "response.audio_transcript.done":
            print("\nAssistant: ", end="", flush=True)

        # 음성 재생
        if response_data.get("type") == "response.audio.delta":
            base64_audio_response = response_data.get("delta")
            if base64_audio_response:
                pcm16_audio = base64_to_pcm16(base64_audio_response)
                await loop.run_in_executor(None, output_stream.write, pcm16_audio)

# 메인 함수 정의
async def main():
    # WebSocket 연결
    async with websockets.connect(WS_URL, additional_headers=HEADERS) as websocket:
        # 초기 요청 전송
        init_request = {
            "type": "response.create",
            "response": {
                "modalities": ["audio", "text"],
                "instructions": "당신은 우수한 AI 어시스턴트입니다.",
                "voice": "alloy"
            }
        }
        await websocket.send(json.dumps(init_request))

        # PyAudio 설정
        CHUNK = 2048              # 청크 크기
        FORMAT = pyaudio.paInt16  # PCM16 형식
        CHANNELS = 1              # 모노
        RATE = 24000              # 샘플링 레이트 (24kHz)

        # PyAudio 인스턴스 준비
        p = pyaudio.PyAudio()

        # 입력 스트림 초기화
        input_stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        # 출력 스트림 초기화
        output_stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK
        )

        try:
            # 음성 송신 태스크와 음성 수신 태스크를 병렬 실행
            print("실시간 대화를 시작합니다.")
            send_task = asyncio.create_task(send_audio(websocket, input_stream, CHUNK))
            receive_task = asyncio.create_task(receive_audio(websocket, output_stream))
            await asyncio.gather(send_task, receive_task)
        except KeyboardInterrupt:
            print("종료합니다.")
        finally:
            # 후처리
            if input_stream.is_active():
                input_stream.stop_stream()
            input_stream.close()
            output_stream.stop_stream()
            output_stream.close()
            p.terminate()

# 메인 함수 실행
if __name__ == "__main__":
    asyncio.run(main())
