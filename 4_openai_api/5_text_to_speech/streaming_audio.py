import asyncio
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

# 클라이언트 준비
openai = AsyncOpenAI()

# 메인 함수 정의
async def main():
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input="나는 고양이로소이다. 이름은 아직 없다.",
        instructions="밝고 긍정적인 어조로 말하세요.",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)

# 메인 함수 실행
if __name__ == "__main__":
    asyncio.run(main())