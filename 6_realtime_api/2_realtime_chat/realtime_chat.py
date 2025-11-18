import asyncio
import websockets
import pyaudio
import base64
import json
import os

# OpenAI APIキーの取得（環境変数から）
API_KEY = os.environ.get("OPENAI_API_KEY")

# WebSocket接続先URLとヘッダー情報
WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "OpenAI-Beta": "realtime=v1"
}

# 音声データをBase64からPCM16に変換
def base64_to_pcm16(base64_audio: str) -> bytes:
    return base64.b64decode(base64_audio)

# 音声入力タスク
async def send_audio(websocket: websockets.WebSocketClientProtocol, stream, chunk_size: int):
     # マイクからの音声を読み取る関数
    def read_audio_block():
        try:
            return stream.read(chunk_size, exception_on_overflow=False)
        except Exception as e:
            print(e)
            return None

    # 音声入力タスクのループ
    while True:
        # マイクからの音声を読み取る
        audio_data = await asyncio.get_event_loop().run_in_executor(None, read_audio_block)
        if audio_data is None:
            continue
        
        # 音声データをPCM16からBase64に変換
        base64_audio = base64.b64encode(audio_data).decode("utf-8")

        # 送信用イベントデータの作成
        audio_event = {
            "type": "input_audio_buffer.append",
            "audio": base64_audio
        }

        # サーバにWebSocketメッセージで送信
        await websocket.send(json.dumps(audio_event))
        await asyncio.sleep(0)

# 音声出力タスク
async def receive_audio(websocket: websockets.WebSocketClientProtocol, output_stream):
    loop = asyncio.get_event_loop()

    # 音声出力タスクのループ
    while True:
        # サーバからのWebSocketメッセージを受信
        response = await websocket.recv()
        response_data = json.loads(response)

        # テキスト表示
        if response_data.get("type") == "response.audio_transcript.delta":
            print(response_data.get("delta", ""), end="", flush=True)
        elif response_data.get("type") == "response.audio_transcript.done":
            print("\nAssistant: ", end="", flush=True)

        # 音声再生
        if response_data.get("type") == "response.audio.delta":
            base64_audio_response = response_data.get("delta")
            if base64_audio_response:
                pcm16_audio = base64_to_pcm16(base64_audio_response)
                await loop.run_in_executor(None, output_stream.write, pcm16_audio)

# メインの定義
async def main():
    # WebSocket接続
    async with websockets.connect(WS_URL, additional_headers=HEADERS) as websocket:
        # 初期リクエストの送信
        init_request = {
            "type": "response.create",
            "response": {
                "modalities": ["audio", "text"],
                "instructions": "あなたは優秀なAIアシスタントです。",
                "voice": "alloy"
            }
        }
        await websocket.send(json.dumps(init_request))

        # PyAudioの設定
        CHUNK = 2048              # チャンクサイズ
        FORMAT = pyaudio.paInt16  # PCM16形式
        CHANNELS = 1              # モノラル
        RATE = 24000              # サンプリングレート（24kHz）

        # PyAudioインスタンスの準備
        p = pyaudio.PyAudio()

        # 入力ストリームの初期化
        input_stream = p.open(
            format=FORMAT,
            channels=CHANNELS, 
            rate=RATE,
            input=True, 
            frames_per_buffer=CHUNK
        )

        # 出力ストリームの初期化
        output_stream = p.open(
            format=FORMAT, 
            channels=CHANNELS, 
            rate=RATE,
            output=True, 
            frames_per_buffer=CHUNK
        )

        try:
            # 音声送信タスクと音声受信タスクを並行実行
            print("リアルタイム会話を開始します。")
            send_task = asyncio.create_task(send_audio(websocket, input_stream, CHUNK))
            receive_task = asyncio.create_task(receive_audio(websocket, output_stream))
            await asyncio.gather(send_task, receive_task)
        except KeyboardInterrupt:
            print("終了します。")
        finally:
            # 後処理
            if input_stream.is_active():
                input_stream.stop_stream()
            input_stream.close()
            output_stream.stop_stream()
            output_stream.close()
            p.terminate()

# メインの実行
if __name__ == "__main__":
    asyncio.run(main())
