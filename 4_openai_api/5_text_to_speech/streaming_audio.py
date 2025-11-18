import asyncio
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

# クライアントの準備
openai = AsyncOpenAI()

# メインの定義
async def main():
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input="ワガハイは猫である。名前はまだない。",
        instructions="明るく前向きな口調で話しましょう。",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)

# メインの実行
if __name__ == "__main__":
    asyncio.run(main())